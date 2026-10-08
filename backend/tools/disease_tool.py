import torch
import torch.nn as nn

from torchvision import models, transforms

from PIL import Image


# ==========================================
# Load Model
# ==========================================

checkpoint = torch.load(

    "models/disease_model.pth",

    map_location="cpu"
)


classes = checkpoint[
    "classes"
]


# ==========================================
# Create ResNet18
# ==========================================

model = models.resnet18(
    weights=None
)


model.fc = nn.Linear(

    model.fc.in_features,

    len(classes)
)


model.load_state_dict(

    checkpoint[
        "model_state_dict"
    ]
)


model.eval()


# ==========================================
# Image Preprocessing
# ==========================================

transform = transforms.Compose([

    transforms.Resize(
        (224, 224)
    ),

    transforms.ToTensor()
])


# ==========================================
# Disease Detection
# ==========================================

def disease_detection_tool(
    image_path
):

    image = Image.open(
        image_path
    ).convert(
        "RGB"
    )


    image_tensor = transform(
        image
    )


    image_tensor = (
        image_tensor.unsqueeze(0)
    )


    with torch.no_grad():

        outputs = model(
            image_tensor
        )


        probabilities = torch.softmax(

            outputs,

            dim=1
        )


        confidence, predicted = torch.max(

            probabilities,

            1
        )


    confidence_value = (
        confidence.item() * 100
    )


    predicted_class = classes[
        predicted.item()
    ]


    if confidence_value < 70:

        return {

            "status":
            "uncertain",

            "disease":
            predicted_class,

            "confidence":
            round(
                confidence_value,
                2
            ),

            "message":
            "Prediction confidence is low. "
            "Please provide a clearer leaf image."
        }


    return {

        "status":
        "success",

        "disease":
        predicted_class,

        "confidence":
        round(
            confidence_value,
            2
        )
    }