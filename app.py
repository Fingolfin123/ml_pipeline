from flask import Flask, request, render_template
import os
# from src.utils import GetProcessorObj
from src.common.exception import CustomException
# from src.utils import load_object
from src.common.type_defs import SourceClassMap

def get_available_source_types():
    return [member.name for member in SourceClassMap]

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

UPLOAD_FOLDER = os.path.join(os.getcwd(), "ml_pipeline", "data")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route('/ingest-data', methods=['GET', 'POST'])
def ingest():
    if request.method == 'POST':
        uploaded_file = request.files.get('file')

        if uploaded_file and uploaded_file.filename != '':
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], uploaded_file.filename)
            # uploaded_file.save(file_path)
            return f"✅ File uploaded to: {file_path}"

        return "⚠️ No file selected."

    # GET request shows the upload form
    return render_template("ingest.html")

@app.route('/train-data', methods=['GET', 'POST'])
def training_datapoint():
    # NOTE: FUTURE PIPELINE UPGRADE --> feature_options should only need to be saved once so 
    # get_raw_features should not be called multiple times
    # Get available features to add as options to html drop down selector
    data_transformation=DataTransformation()
    feature_options = data_transformation.get_raw_features()
    if request.method == 'GET':
        # Add available features to html drop down selections
        return render_template("train.html", features=feature_options)

    else:
        # Get selected feature from html drop down selection
        selected_feature = request.form.get('features')
        print(f"the selected feature is: {selected_feature}")
        selected_feature = selected_feature.replace(" (numerical)", "").replace(" (categorical)", "")

        # Create training model using the selected feature
        # NOTE: Selected training model is from best performing model in model evalutaion 'results'
        training_pipeline = TrainingPipeline()
        results = training_pipeline.training(selected_feature)
        print(f"the results are: {results}")

        return render_template("train.html", features=feature_options, results=results)


@app.route('/predict-data', methods=['GET', 'POST'])
def predict_datapoint():
    # NOTE: FUTURE PIPELINE UPGRADE --> need to know which model to use in predictions
    # currently have to hardcode "target_feature_name"
    model_path = os.path.join('artifacts', 'model_Linear Regression.joblib')
    preproc_path = os.path.join('artifacts', 'pre_proc.joblib')
    predict_pipeline = PredictPipeline(model_path, preproc_path)

    if request.method == 'GET':
        # Load preprocessor and get options
        pre_processor_obj = GetProcessorObj(
            proc_obj_path=preproc_path,
            target_feature_name="math_score"
        )
        return render_template("predict.html", options=pre_processor_obj.feature_options)

    else:
        data = PredictionSelectionData(
            gender=request.form.get('gender'),
            race_ethnicity=request.form.get('race_ethnicity'),
            parental_level_of_education=request.form.get('parental_level_of_education'),
            lunch=request.form.get('lunch'),
            test_preparation_course=request.form.get('test_preparation_course'),
            reading_score=request.form.get('reading_score'),
            writing_score=request.form.get('writing_score'),
        )

        pred_df = data.get_data_as_data_frame()
        print(f"the selected features are: {pred_df}")
        results = predict_pipeline.predict(pred_df, 'math_score')
        print(f"the prediction is: {results}")
        pre_processor_obj = GetProcessorObj(
            proc_obj_path=preproc_path,
            target_feature_name="math_score"
        )        
        return render_template('predict.html', options=pre_processor_obj.feature_options, results=results[0])


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
