from pathlib import Path
import random
import cv2


CLASS_NAMES = [
    "missing_hole",
    "mouse_bite",
    "open_circuit",
    "short",
    "spur",
    "spurious_copper",
]


def draw_yolo_boxes(image, label_path):
    height, width = image.shape[:2]

    if not label_path.exists():
        return image

    lines = label_path.read_text(
        encoding="utf-8"
    ).strip().splitlines()

    for line in lines:

        parts = line.split()

        if len(parts) != 5:
            continue

        class_id = int(parts[0])

        x_center = float(parts[1])
        y_center = float(parts[2])
        box_width = float(parts[3])
        box_height = float(parts[4])

        # Convert normalized YOLO coordinates
        # back to pixel coordinates.
        x_center *= width
        y_center *= height
        box_width *= width
        box_height *= height

        x1 = int(x_center - box_width / 2)
        y1 = int(y_center - box_height / 2)
        x2 = int(x_center + box_width / 2)
        y2 = int(y_center + box_height / 2)

        # Keep coordinates inside image.
        x1 = max(0, min(x1, width - 1))
        y1 = max(0, min(y1, height - 1))
        x2 = max(0, min(x2, width - 1))
        y2 = max(0, min(y2, height - 1))

        class_name = (
            CLASS_NAMES[class_id]
            if 0 <= class_id < len(CLASS_NAMES)
            else f"class_{class_id}"
        )

        # Draw bounding box.
        cv2.rectangle(
            image,
            (x1, y1),
            (x2, y2),
            (0, 255, 0),
            3,
        )

        # Draw label.
        cv2.putText(
            image,
            class_name,
            (x1, max(30, y1 - 10)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2,
            cv2.LINE_AA,
        )

    return image


def main():

    dataset_root = Path("dataset/yolo")

    output_root = Path(
        "dataset/visualizations"
    )

    output_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    random.seed(42)

    for split in ["train", "val", "test"]:

        image_dir = (
            dataset_root
            / "images"
            / split
        )

        label_dir = (
            dataset_root
            / "labels"
            / split
        )

        images = sorted(
            list(image_dir.glob("*.jpg"))
            + list(image_dir.glob("*.jpeg"))
            + list(image_dir.glob("*.png"))
        )

        if not images:
            print(
                f"No images found in {image_dir}"
            )
            continue

        # Select up to 10 random images.
        selected = random.sample(
            images,
            min(10, len(images)),
        )

        split_output = (
            output_root / split
        )

        split_output.mkdir(
            parents=True,
            exist_ok=True,
        )

        print(
            f"\n{split.upper()}: "
            f"visualizing {len(selected)} images"
        )

        for image_path in selected:

            label_path = (
                label_dir
                / f"{image_path.stem}.txt"
            )

            image = cv2.imread(
                str(image_path)
            )

            if image is None:
                print(
                    f"Could not read: {image_path}"
                )
                continue

            image = draw_yolo_boxes(
                image,
                label_path,
            )

            output_path = (
                split_output
                / image_path.name
            )

            cv2.imwrite(
                str(output_path),
                image,
            )

    print(
        "\nVisualization complete."
    )

    print(
        f"Open this folder:\n"
        f"{output_root.resolve()}"
    )


if __name__ == "__main__":
    main()