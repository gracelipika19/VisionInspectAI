from __future__ import annotations

import argparse
import json
import random
import shutil
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

CLASS_NAMES = [
    "missing_hole",
    "mouse_bite",
    "open_circuit",
    "short",
    "spur",
    "spurious_copper",
]

CLASS_TO_ID = {
    class_name: idx
    for idx, class_name in enumerate(CLASS_NAMES)
}

# Explicit mapping because dataset folder names use capitals/underscores.
FOLDER_TO_CLASS = {
    "Missing_hole": "missing_hole",
    "Mouse_bite": "mouse_bite",
    "Open_circuit": "open_circuit",
    "Short": "short",
    "Spur": "spur",
    "Spurious_copper": "spurious_copper",
}


# ============================================================
# DATA STRUCTURES
# ============================================================

@dataclass
class BoundingBox:
    class_name: str
    xmin: float
    ymin: float
    xmax: float
    ymax: float


@dataclass
class Sample:
    image_path: Path
    xml_path: Path
    folder_class: str
    width: int
    height: int
    objects: list[BoundingBox]


# ============================================================
# HELPERS
# ============================================================

def normalize_class_name(value: str) -> str:
    """Normalize annotation class names."""
    return (
        value.strip()
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
    )


def parse_float(value: str, field_name: str, xml_path: Path) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        raise ValueError(
            f"Invalid {field_name} value in {xml_path}: {value!r}"
        )


def validate_bbox(
    bbox: BoundingBox,
    width: int,
    height: int,
    xml_path: Path,
) -> None:
    """Validate Pascal VOC bounding box coordinates."""

    if not (0 <= bbox.xmin < bbox.xmax <= width):
        raise ValueError(
            f"Invalid X coordinates in {xml_path}: "
            f"({bbox.xmin}, {bbox.xmax}) for width={width}"
        )

    if not (0 <= bbox.ymin < bbox.ymax <= height):
        raise ValueError(
            f"Invalid Y coordinates in {xml_path}: "
            f"({bbox.ymin}, {bbox.ymax}) for height={height}"
        )


# ============================================================
# XML PARSING
# ============================================================

def parse_annotation(
    xml_path: Path,
    expected_class: str,
) -> tuple[int, int, list[BoundingBox]]:
    """
    Parse a Pascal VOC XML annotation.

    Returns:
        width, height, list of bounding boxes
    """

    try:
        tree = ET.parse(xml_path)
    except ET.ParseError as exc:
        raise ValueError(f"Invalid XML: {xml_path}") from exc

    root = tree.getroot()

    size = root.find("size")

    if size is None:
        raise ValueError(f"Missing <size> section in {xml_path}")

    width_text = size.findtext("width")
    height_text = size.findtext("height")

    if width_text is None or height_text is None:
        raise ValueError(
            f"Missing image dimensions in {xml_path}"
        )

    width = int(width_text)
    height = int(height_text)

    if width <= 0 or height <= 0:
        raise ValueError(
            f"Invalid image dimensions in {xml_path}: "
            f"{width}x{height}"
        )

    objects = []

    xml_objects = root.findall("object")

    if not xml_objects:
        raise ValueError(
            f"No <object> annotations found in {xml_path}"
        )

    for obj in xml_objects:

        name = obj.findtext("name")

        if not name:
            raise ValueError(
                f"Object without class name in {xml_path}"
            )

        class_name = normalize_class_name(name)

        if class_name not in CLASS_TO_ID:
            raise ValueError(
                f"Unknown class '{name}' in {xml_path}. "
                f"Expected one of: {CLASS_NAMES}"
            )

        # The dataset folders are class-specific.
        # Make sure annotation class agrees with folder class.
        if class_name != expected_class:
            raise ValueError(
                f"Class mismatch in {xml_path}: "
                f"folder={expected_class}, annotation={class_name}"
            )

        bbox_node = obj.find("bndbox")

        if bbox_node is None:
            raise ValueError(
                f"Missing <bndbox> in {xml_path}"
            )

        xmin = parse_float(
            bbox_node.findtext("xmin"),
            "xmin",
            xml_path,
        )

        ymin = parse_float(
            bbox_node.findtext("ymin"),
            "ymin",
            xml_path,
        )

        xmax = parse_float(
            bbox_node.findtext("xmax"),
            "xmax",
            xml_path,
        )

        ymax = parse_float(
            bbox_node.findtext("ymax"),
            "ymax",
            xml_path,
        )

        bbox = BoundingBox(
            class_name=class_name,
            xmin=xmin,
            ymin=ymin,
            xmax=xmax,
            ymax=ymax,
        )

        validate_bbox(
            bbox,
            width,
            height,
            xml_path,
        )

        objects.append(bbox)

    return width, height, objects


# ============================================================
# DATASET DISCOVERY
# ============================================================

def discover_samples(source_root: Path) -> list[Sample]:

    images_root = source_root / "images"
    annotations_root = source_root / "Annotations"

    if not images_root.exists():
        raise FileNotFoundError(
            f"Images directory not found: {images_root}"
        )

    if not annotations_root.exists():
        raise FileNotFoundError(
            f"Annotations directory not found: {annotations_root}"
        )

    samples = []
    seen_images = set()

    print("\nDiscovering dataset...")

    for folder_name, class_name in FOLDER_TO_CLASS.items():

        annotation_dir = annotations_root / folder_name
        image_dir = images_root / folder_name

        if not annotation_dir.exists():
            raise FileNotFoundError(
                f"Annotation folder not found: {annotation_dir}"
            )

        if not image_dir.exists():
            raise FileNotFoundError(
                f"Image folder not found: {image_dir}"
            )

        xml_files = sorted(annotation_dir.glob("*.xml"))

        print(
            f"  {class_name:<18} "
            f"{len(xml_files):>4} annotations"
        )

        for xml_path in xml_files:

            # Read filename from XML
            tree = ET.parse(xml_path)
            root = tree.getroot()

            filename = root.findtext("filename")

            if not filename:
                raise ValueError(
                    f"Missing <filename> in {xml_path}"
                )

            image_path = image_dir / filename

            if not image_path.exists():
                raise FileNotFoundError(
                    f"Image referenced by XML does not exist:\n"
                    f"XML: {xml_path}\n"
                    f"Image: {image_path}"
                )

            resolved_image = image_path.resolve()

            if resolved_image in seen_images:
                raise ValueError(
                    f"Duplicate image referenced by annotations: "
                    f"{image_path}"
                )

            seen_images.add(resolved_image)

            width, height, objects = parse_annotation(
                xml_path,
                class_name,
            )

            samples.append(
                Sample(
                    image_path=image_path,
                    xml_path=xml_path,
                    folder_class=class_name,
                    width=width,
                    height=height,
                    objects=objects,
                )
            )

    return samples


# ============================================================
# DATASET SPLIT
# ============================================================

def split_dataset(
    samples: list[Sample],
    train_ratio: float,
    val_ratio: float,
    test_ratio: float,
    seed: int,
) -> dict[str, list[Sample]]:

    if abs(
        train_ratio + val_ratio + test_ratio - 1.0
    ) > 1e-9:
        raise ValueError(
            "Train/validation/test ratios must sum to 1.0"
        )

    grouped = defaultdict(list)

    for sample in samples:
        grouped[sample.folder_class].append(sample)

    rng = random.Random(seed)

    splits = {
        "train": [],
        "val": [],
        "test": [],
    }

    for class_name in CLASS_NAMES:

        class_samples = grouped[class_name]

        rng.shuffle(class_samples)

        total = len(class_samples)

        train_count = int(total * train_ratio)
        val_count = int(total * val_ratio)

        train_samples = class_samples[
            :train_count
        ]

        val_samples = class_samples[
            train_count:train_count + val_count
        ]

        test_samples = class_samples[
            train_count + val_count:
        ]

        splits["train"].extend(train_samples)
        splits["val"].extend(val_samples)
        splits["test"].extend(test_samples)

    # Shuffle each split again so classes are not grouped together.
    for split_samples in splits.values():
        rng.shuffle(split_samples)

    return splits


# ============================================================
# YOLO CONVERSION
# ============================================================

def bbox_to_yolo(
    bbox: BoundingBox,
    image_width: int,
    image_height: int,
) -> str:

    x_center = (
        (bbox.xmin + bbox.xmax) / 2.0
    ) / image_width

    y_center = (
        (bbox.ymin + bbox.ymax) / 2.0
    ) / image_height

    box_width = (
        bbox.xmax - bbox.xmin
    ) / image_width

    box_height = (
        bbox.ymax - bbox.ymin
    ) / image_height

    values = [
        x_center,
        y_center,
        box_width,
        box_height,
    ]

    # Safety validation.
    for value in values:
        if value < -1e-6 or value > 1.000001:
            raise ValueError(
                f"Invalid normalized YOLO value: {value}"
            )

    class_id = CLASS_TO_ID[bbox.class_name]

    return (
        f"{class_id} "
        f"{x_center:.6f} "
        f"{y_center:.6f} "
        f"{box_width:.6f} "
        f"{box_height:.6f}"
    )


# ============================================================
# OUTPUT
# ============================================================

def prepare_output_directories(output_root: Path) -> None:

    for split in ["train", "val", "test"]:

        (output_root / "images" / split).mkdir(
            parents=True,
            exist_ok=True,
        )

        (output_root / "labels" / split).mkdir(
            parents=True,
            exist_ok=True,
        )


def copy_sample(
    sample: Sample,
    split: str,
    output_root: Path,
) -> None:

    # Prefix with class to guarantee unique output filenames.
    unique_stem = (
        f"{sample.folder_class}__"
        f"{sample.image_path.stem}"
    )

    image_destination = (
        output_root
        / "images"
        / split
        / f"{unique_stem}{sample.image_path.suffix.lower()}"
    )

    label_destination = (
        output_root
        / "labels"
        / split
        / f"{unique_stem}.txt"
    )

    shutil.copy2(
        sample.image_path,
        image_destination,
    )

    label_lines = []

    for bbox in sample.objects:

        label_lines.append(
            bbox_to_yolo(
                bbox,
                sample.width,
                sample.height,
            )
        )

    label_destination.write_text(
        "\n".join(label_lines) + "\n",
        encoding="utf-8",
    )


# ============================================================
# STATISTICS
# ============================================================

def calculate_statistics(
    splits: dict[str, list[Sample]]
) -> dict:

    statistics = {}

    for split_name, samples in splits.items():

        image_counts = Counter(
            sample.folder_class
            for sample in samples
        )

        object_counts = Counter()

        for sample in samples:
            for obj in sample.objects:
                object_counts[obj.class_name] += 1

        statistics[split_name] = {
            "images": dict(
                sorted(image_counts.items())
            ),
            "objects": dict(
                sorted(object_counts.items())
            ),
            "total_images": len(samples),
            "total_objects": sum(
                object_counts.values()
            ),
        }

    return statistics


def print_statistics(
    statistics: dict,
) -> None:

    print("\n" + "=" * 70)
    print("DATASET SPLIT STATISTICS")
    print("=" * 70)

    for split in ["train", "val", "test"]:

        info = statistics[split]

        print(
            f"\n{split.upper()}: "
            f"{info['total_images']} images | "
            f"{info['total_objects']} objects"
        )

        print("  Image counts by class:")

        for class_name in CLASS_NAMES:

            count = info["images"].get(
                class_name,
                0,
            )

            print(
                f"    {class_name:<18}: {count}"
            )

        print("  Object counts by class:")

        for class_name in CLASS_NAMES:

            count = info["objects"].get(
                class_name,
                0,
            )

            print(
                f"    {class_name:<18}: {count}"
            )


# ============================================================
# DATA.YAML
# ============================================================

def write_data_yaml(
    output_root: Path,
) -> None:

    yaml_content = """path: .
train: images/train
val: images/val
test: images/test

names:
  0: missing_hole
  1: mouse_bite
  2: open_circuit
  3: short
  4: spur
  5: spurious_copper
"""

    (output_root / "data.yaml").write_text(
        yaml_content,
        encoding="utf-8",
    )


# ============================================================
# MAIN
# ============================================================

def main():

    parser = argparse.ArgumentParser(
        description=(
            "Convert Peking University PCB defect "
            "Pascal VOC annotations to YOLO format."
        )
    )

    parser.add_argument(
        "--source",
        required=True,
        help="Path to PCB_DATASET directory",
    )

    parser.add_argument(
        "--output",
        default="dataset/yolo",
        help="Output YOLO dataset directory",
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed",
    )

    parser.add_argument(
        "--train-ratio",
        type=float,
        default=0.70,
        help="Training split ratio",
    )

    parser.add_argument(
        "--val-ratio",
        type=float,
        default=0.20,
        help="Validation split ratio",
    )

    parser.add_argument(
        "--test-ratio",
        type=float,
        default=0.10,
        help="Test split ratio",
    )

    parser.add_argument(
        "--clean",
        action="store_true",
        help="Delete existing output directory first",
    )

    args = parser.parse_args()

    source_root = Path(
        args.source
    ).expanduser().resolve()

    output_root = Path(
        args.output
    ).expanduser().resolve()

    # Safety check.
    if source_root == output_root:
        raise ValueError(
            "Source and output directories cannot be the same."
        )

    if output_root.exists():

        if not args.clean:
            raise FileExistsError(
                f"\nOutput directory already exists:\n"
                f"{output_root}\n\n"
                f"If you want to regenerate it, run again "
                f"with --clean."
            )

        print(
            f"\nRemoving existing generated dataset:\n"
            f"{output_root}"
        )

        shutil.rmtree(output_root)

    print("\n" + "=" * 70)
    print("VISIONINSPECT AI — PCB DATASET PREPARATION")
    print("=" * 70)

    print(f"\nSource : {source_root}")
    print(f"Output : {output_root}")
    print(f"Seed   : {args.seed}")

    print(
        "\nUsing ONLY the original 'images/' directory."
    )

    print(
        "Ignoring 'rotation/' and 'PCB_USED/' "
        "for the initial dataset."
    )

    # --------------------------------------------------------
    # 1. Discover and validate samples
    # --------------------------------------------------------

    samples = discover_samples(source_root)

    print(
        f"\nTotal validated image/XML pairs: "
        f"{len(samples)}"
    )

    if len(samples) == 0:
        raise ValueError(
            "No dataset samples found."
        )

    # --------------------------------------------------------
    # 2. Split
    # --------------------------------------------------------

    splits = split_dataset(
        samples=samples,
        train_ratio=args.train_ratio,
        val_ratio=args.val_ratio,
        test_ratio=args.test_ratio,
        seed=args.seed,
    )

    # --------------------------------------------------------
    # 3. Create output directories
    # --------------------------------------------------------

    prepare_output_directories(
        output_root
    )

    # --------------------------------------------------------
    # 4. Copy images + generate YOLO labels
    # --------------------------------------------------------

    print("\nConverting annotations to YOLO format...")

    for split_name in ["train", "val", "test"]:

        for sample in splits[split_name]:

            copy_sample(
                sample,
                split_name,
                output_root,
            )

    # --------------------------------------------------------
    # 5. Create data.yaml
    # --------------------------------------------------------

    write_data_yaml(
        output_root
    )

    # --------------------------------------------------------
    # 6. Statistics
    # --------------------------------------------------------

    statistics = calculate_statistics(
        splits
    )

    print_statistics(
        statistics
    )

    # --------------------------------------------------------
    # 7. Save report
    # --------------------------------------------------------

    report = {
        "dataset": "Peking University PCB Defects",
        "source": str(source_root),
        "output": str(output_root),
        "seed": args.seed,
        "split_ratios": {
            "train": args.train_ratio,
            "val": args.val_ratio,
            "test": args.test_ratio,
        },
        "classes": CLASS_TO_ID,
        "statistics": statistics,
    }

    report_path = (
        output_root / "dataset_summary.json"
    )

    report_path.write_text(
        json.dumps(
            report,
            indent=2,
        ),
        encoding="utf-8",
    )

    # --------------------------------------------------------
    # DONE
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("DATASET PREPARATION COMPLETE")
    print("=" * 70)

    print(
        f"\nYOLO dataset created at:\n"
        f"{output_root}"
    )

    print(
        f"\nYOLO config:\n"
        f"{output_root / 'data.yaml'}"
    )

    print(
        f"\nDataset report:\n"
        f"{report_path}"
    )

    print(
        "\nNext step: visually verify bounding boxes "
        "before training YOLO."
    )


if __name__ == "__main__":
    main()