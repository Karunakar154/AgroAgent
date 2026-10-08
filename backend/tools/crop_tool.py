import joblib
import pandas as pd


model = joblib.load(
    "models/crop_recommendation_model.pkl"
)


def crop_recommendation_tool(

    nitrogen,

    phosphorus,

    potassium,

    temperature,

    humidity,

    ph,

    rainfall

):

    data = pd.DataFrame([{

        "N": nitrogen,

        "P": phosphorus,

        "K": potassium,

        "temperature":
        temperature,

        "humidity":
        humidity,

        "ph":
        ph,

        "rainfall":
        rainfall

    }])


    prediction = model.predict(
        data
    )[0]


    return {

        "recommended_crop":
        prediction
    }