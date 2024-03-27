import os
import pandas as pd


def process_csv_files(folder_path):
    combined_data = pd.DataFrame()

    # Loop through each file in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith(".csv"):
            file_path = os.path.join(folder_path, filename)
            fingering = filename.split("_")[-1].split(".")[0]
            df = pd.read_csv(
                file_path,
                skiprows=1,
                header=None,
                names=["Frame", "Hand", "Landmark", "X", "Y", "Z", "Fingering"],
            )
            frame_counts = df.groupby("Frame").size()

            # Filter out frames with exactly 42 rows (2 hands * 21 landmarks)
            valid_frames = frame_counts[frame_counts == 42].index

            df = df[df["Frame"].isin(valid_frames)]
            df["Fingering"] = fingering
            combined_data = pd.concat([combined_data, df], ignore_index=True)

    return combined_data


def generate_unique_frames_across_videos(frame_column):
    output = []
    prev_frame = 0
    next_index = 0

    for frame in frame_column:
        if frame != prev_frame:
            next_index += 1
        output.append(next_index)
        prev_frame = frame

    return output


def flatten_data(data):
    data = pd.read_csv("combined_data_unique_frames.csv")
    data["Landmark_Hand"] = data["Landmark"] + "_" + data["Hand"]
    pivot_data = data.pivot(
        index="Unique_Frame",
        columns="Landmark_Hand",
        values=["X", "Y", "Z", "Fingering"],
    )

    # Flatten the MultiIndex columns
    pivot_data.columns = [
        f"{col[1]}_{col[0]}" if col[0] != "Fingering" else "Fingering"
        for col in pivot_data.columns
    ]

    pivot_data = pivot_data.loc[:, ~pivot_data.columns.duplicated()]
    pivot_data.reset_index(inplace=True)

    return pivot_data


# Path to the folder containing CSV files
folder_path = "landmark_data_stable"

# Combine data to one csv file
combined_data = process_csv_files(folder_path)
combined_data.to_csv("combined_data_filtered.csv", index=False)
print("Combined data saved to 'combined_data_filtered.csv'")


# Apply the function to generate unique frame numbers across videos
data = pd.read_csv("combined_data_filtered.csv")
data["Unique_Frame"] = generate_unique_frames_across_videos(data["Frame"])
data.to_csv("combined_data_unique_frames.csv", index=False)


# Save to CSV
data = pd.read_csv("combined_data_unique_frames.csv")
data = flatten_data(data)
data.to_csv("flattened_data.csv", index=False)
