import { useEffect, useRef, useState } from "react";

function DetectionOverlay({
  imageUrl,
  imageWidth,
  imageHeight,
  detections,
}) {
  const imageRef = useRef(null);

  const [displaySize, setDisplaySize] = useState({
    width: 0,
    height: 0,
  });

  const updateDisplaySize = () => {
    if (!imageRef.current) {
      return;
    }

    setDisplaySize({
      width: imageRef.current.clientWidth,
      height: imageRef.current.clientHeight,
    });
  };

  useEffect(() => {
    updateDisplaySize();

    window.addEventListener("resize", updateDisplaySize);

    return () => {
      window.removeEventListener("resize", updateDisplaySize);
    };
  }, [imageUrl]);

  const scaleX =
    imageWidth > 0
      ? displaySize.width / imageWidth
      : 1;

  const scaleY =
    imageHeight > 0
      ? displaySize.height / imageHeight
      : 1;

  return (
    <div className="detection-container">
      <img
        ref={imageRef}
        src={imageUrl}
        alt="PCB inspection"
        className="inspection-image"
        onLoad={updateDisplaySize}
      />

      {displaySize.width > 0 &&
        detections.map((detection, index) => {
          const [x1, y1, x2, y2] = detection.bbox;

          const left = x1 * scaleX;
          const top = y1 * scaleY;

          const width = (x2 - x1) * scaleX;
          const height = (y2 - y1) * scaleY;

          return (
            <div
              key={index}
              className="detection-box"
              style={{
                left: `${left}px`,
                top: `${top}px`,
                width: `${width}px`,
                height: `${height}px`,
              }}
            >
              <span className="detection-label">
                {detection.class_name.replaceAll("_", " ")}{" "}
                {(detection.confidence * 100).toFixed(1)}%
              </span>
            </div>
          );
        })}
    </div>
  );
}

export default DetectionOverlay;