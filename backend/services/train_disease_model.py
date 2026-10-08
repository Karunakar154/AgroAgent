import os
import torch
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader, Subset, random_split
import torch.nn as nn
import torch.optim as optim


# -----------------------------
# Device
# -----------------------------
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

print("Using device:", device)


# -----------------------------
# Image transformation
# -----------------------------
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(),
    transforms.ToTensor()
])


# -----------------------------
# Load dataset
# -----------------------------
full_dataset = datasets.ImageFolder(
    "data/plant_disease",
    transform=transform
)

print("Total images:", len(full_dataset))
print("Total classes:", len(full_dataset.classes))


# -----------------------------
# Select only 100 images/class
# -----------------------------
images_per_class = 100

selected_indices = []

class_counts = {
    class_id: 0
    for class_id in range(len(full_dataset.classes))
}

for index, (_, class_id) in enumerate(full_dataset.samples):

    if class_counts[class_id] < images_per_class:
        selected_indices.append(index)
        class_counts[class_id] += 1


dataset = Subset(
    full_dataset,
    selected_indices
)

print("Images selected:", len(dataset))


# -----------------------------
# Train / validation split
# -----------------------------
train_size = int(0.8 * len(dataset))
val_size = len(dataset) - train_size

train_dataset, val_dataset = random_split(
    dataset,
    [train_size, val_size],
    generator=torch.Generator().manual_seed(42)
)


# -----------------------------
# Data loaders
# -----------------------------
train_loader = DataLoader(
    train_dataset,
    batch_size=16,
    shuffle=True
)

val_loader = DataLoader(
    val_dataset,
    batch_size=16,
    shuffle=False
)


# -----------------------------
# Load pretrained ResNet18
# -----------------------------
model = models.resnet18(weights="DEFAULT")


# Freeze ResNet layers
for parameter in model.parameters():
    parameter.requires_grad = False


# Replace final layer
num_classes = len(full_dataset.classes)

model.fc = nn.Linear(
    model.fc.in_features,
    num_classes
)

model = model.to(device)


# -----------------------------
# Loss and optimizer
# -----------------------------
criterion = nn.CrossEntropyLoss()

optimizer = optim.Adam(
    model.fc.parameters(),
    lr=0.001
)


# -----------------------------
# Training
# -----------------------------
epochs = 5

for epoch in range(epochs):

    model.train()

    running_loss = 0.0

    for images, labels in train_loader:

        images = images.to(device)
        labels = labels.to(device)

        optimizer.zero_grad()

        outputs = model(images)

        loss = criterion(outputs, labels)

        loss.backward()

        optimizer.step()

        running_loss += loss.item()

    average_loss = running_loss / len(train_loader)

    print(
        f"Epoch [{epoch + 1}/{epochs}] "
        f"Loss: {average_loss:.4f}"
    )


# -----------------------------
# Save model
# -----------------------------
os.makedirs("models", exist_ok=True)

torch.save(
    {
        "model_state_dict": model.state_dict(),
        "classes": full_dataset.classes
    },
    "models/disease_model.pth"
)

print("Disease model saved successfully!")