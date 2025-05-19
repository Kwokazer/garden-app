#!/bin/bash

RECORDINGS_DIR="/config/recordings"
PROCESSED_DIR="/config/recordings/processed"
FAILED_DIR="/config/recordings/failed"

mkdir -p $PROCESSED_DIR
mkdir -p $FAILED_DIR

echo "Finalizing recording $1"

RECORDING_DIR="$RECORDINGS_DIR/$1"

if [ -f "$RECORDING_DIR/recording.mp4" ]; then
    # Успешная запись
    echo "Recording completed successfully, moving to processed directory"
    mv "$RECORDING_DIR" "$PROCESSED_DIR/"
    exit 0
else
    # Ошибка записи
    echo "Recording failed, moving to failed directory"
    mv "$RECORDING_DIR" "$FAILED_DIR/"
    exit 1
fi