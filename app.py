import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from flask import Flask, request, render_template

from src.common.type_defs import SourceClassMap
from src.components.ingestion.ingestion import IngestionManager
from src.components.transformation.transformation import DataTransformation
from src.pipelines.predict_pipeline import PredictionSelectionData, PredictPipeline
from src.pipelines.training_pipeline import TrainingPipeline

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


UPLOAD_FOLDER = "data"
MODEL_RUN_FOLDER = "model_run"
EDA_FOLDER = "static/eda_results"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MODEL_RUN_FOLDER"] = MODEL_RUN_FOLDER
app.config["EDA_FOLDER"] = EDA_FOLDER


@app.route("/ingest-data", methods=["GET", "POST"])
def ingest():
    message = None
    eda_head = None
    eda_shape = None
    eda_images = []
    eda_summary = None

    if request.method == "POST":
        uploaded_file = request.files.get("file")

        if uploaded_file and uploaded_file.filename != "":
            # Extract file extension
            ext = uploaded_file.filename.rsplit(".", 1)[-1]

            try:
                source_enum = SourceClassMap.from_extension(ext)
            except ValueError as e:
                return str(e), 400

            # Save uploaded file
            file_path = os.path.join(
                app.config["UPLOAD_FOLDER"], uploaded_file.filename
            )

            # Run ingestion
            obj = IngestionManager()
            obj.set_ingest_path(path=file_path)
            df_raw, df_train, df_test = obj.run()

            message = f"""✅ File ingested into raw, training, and testing tables to temp project folder '{app.config["MODEL_RUN_FOLDER"]}/'. """

            # Run EDA
            eda_head, eda_shape, eda_images, eda_summary = run_full_eda(df_raw)

        else:
            message = "⚠️ No file selected."

    return render_template(
        "ingest.html",
        message=message,
        eda_head=eda_head,
        eda_shape=eda_shape,
        eda_images=eda_images,
        eda_summary=eda_summary,
    )

def run_full_eda(df: pd.DataFrame):
    os.makedirs(app.config["EDA_FOLDER"], exist_ok=True)
    eda_images = []

    # Show first few rows
    eda_head = df.head().to_html(classes="table table-striped table-bordered", border=0)

    # Show shape
    eda_shape = f"Rows: {df.shape[0]}, Columns: {df.shape[1]}"

    # Summary statistics
    eda_df = df.describe(include="all")

    # Add a row for null counts
    eda_df.loc["null_count"] = df.isnull().sum()

    # Convert to HTML
    eda_summary = eda_df.to_html(classes="table table-striped table-bordered", border=0)

    # Numeric columns
    numeric_cols = df.select_dtypes(include="number").columns

    for num_col in numeric_cols:
        plt.figure(figsize=(8, 6))
        sns.histplot(df[num_col], kde=True, color="blue")
        plt.title(f"Distribution of {num_col}")
        filename = f"{num_col}_distribution.png"
        save_path = os.path.join(app.config["EDA_FOLDER"], filename)
        plt.savefig(save_path)
        plt.close()

        # Store relative path for HTML
        eda_images.append(f"static/eda_results/{filename}")

    if len(numeric_cols) > 1:
        plt.figure(figsize=(10, 8))
        sns.heatmap(df[numeric_cols].corr(), annot=True, cmap="coolwarm")
        filename = "correlation_heatmap.png"
        save_path = os.path.join(app.config["EDA_FOLDER"], filename)
        plt.savefig(save_path)
        plt.close()

        # Store relative path for HTML
        eda_images.append(f"static/eda_results/{filename}")

    return eda_head, eda_shape, eda_images, eda_summary

@app.route("/transform-data", methods=["GET", "POST"])
def transform_datapoint():
    # Initialize DataTransformation and get available features for dropdown
    data_transformation = DataTransformation()
    feature_options = data_transformation.get_raw_features()

    if request.method == "POST":
        # Get selected feature from HTML dropdown
        selected_feature = request.form.get("features")
        if not selected_feature:
            return render_template(
                "transform.html",
                features=feature_options,
                message="⚠️ Please select a feature before proceeding."
            )

        # Clean feature name (remove '(numerical)' / '(categorical)')
        selected_feature = selected_feature.replace(" (numerical)", "").replace(
            " (categorical)", ""
        )
        print(f"Selected target feature: {selected_feature}")

        # Create preprocessing object using the selected feature
        try:
            data_transformation.run(selected_feature)
            message = f"✅ Preprocessor object successfully built for target feature: '{selected_feature}'."
        except Exception as e:
            message = f"❌ Failed to build preprocessor for '{selected_feature}': {str(e)}"
        print(f"Selected target feature: {selected_feature}")
        # Return template with confirmation message
        return render_template(
            "transform.html",
            features=feature_options,
            message=message
        )

    # GET request: Just show dropdown without message
    return render_template("transform.html", features=feature_options)


@app.route("/train-data", methods=["GET", "POST"])
def training_datapoint():
    # NOTE: FUTURE PIPELINE UPGRADE --> feature_options should only need to be saved once so
    # get_raw_features should not be called multiple times
    # Get available features to add as options to html drop down selector
    data_transformation = DataTransformation()
    feature_options = data_transformation.get_raw_features()
    if request.method == "POST":
        # Get selected feature from html drop down selection
        selected_feature = request.form.get("features")
        print(f"the selected feature is: {selected_feature}")
        selected_feature = selected_feature.replace(" (numerical)", "").replace(
            " (categorical)", ""
        )

        # # Create training model using the selected feature
        # # NOTE: Selected training model is from best performing model in model evalutaion 'results'
        # training_pipeline = TrainingPipeline()
        # results = training_pipeline.training(selected_feature)
        # print(f"the results are: {results}")

        # return render_template("train.html", features=feature_options, results=results)
        return render_template("transform.html", features=feature_options)
    
    else:
        # Add available features to html drop down selections
        return render_template("transform.html", features=feature_options)

@app.route("/predict-data", methods=["GET", "POST"])
def predict_datapoint():
    # NOTE: FUTURE PIPELINE UPGRADE --> need to know which model to use in predictions
    # currently have to hardcode "target_feature_name"
    model_path = os.path.join("model_run", "model_Linear Regression.joblib")
    preproc_path = os.path.join("model_run", "pre_proc.joblib")
    predict_pipeline = PredictPipeline(model_path, preproc_path)

    if request.method == "GET":
        # Load preprocessor and get options
        pre_processor_obj = GetProcessorObj(
            proc_obj_path=preproc_path, target_feature_name="math_score"
        )
        return render_template(
            "predict.html", options=pre_processor_obj.feature_options
        )

    else:
        data = PredictionSelectionData(
            gender=request.form.get("gender"),
            race_ethnicity=request.form.get("race_ethnicity"),
            parental_level_of_education=request.form.get("parental_level_of_education"),
            lunch=request.form.get("lunch"),
            test_preparation_course=request.form.get("test_preparation_course"),
            reading_score=request.form.get("reading_score"),
            writing_score=request.form.get("writing_score"),
        )

        pred_df = data.get_data_as_data_frame()
        print(f"the selected features are: {pred_df}")
        results = predict_pipeline.predict(pred_df, "math_score")
        print(f"the prediction is: {results}")
        pre_processor_obj = GetProcessorObj(
            proc_obj_path=preproc_path, target_feature_name="math_score"
        )
        return render_template(
            "predict.html",
            options=pre_processor_obj.feature_options,
            results=results[0],
        )


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
