#!/usr/bin/env bash
set -euo pipefail

PYBIN=${PYBIN:-python3}
APP_NAME="Anora Editor"
EXEC_PATH="${PYBIN} \"$(readlink -f anora_editor.py)\" %F"
DESKTOP_ID="anora-editor.desktop"
DESKTOP_FILE="$HOME/.local/share/applications/${DESKTOP_ID}"
ICON_PATH="$(readlink -f anora_icon.png || true)"

mkdir -p "$(dirname "$DESKTOP_FILE")"

cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Type=Application
Name=${APP_NAME}
Comment=Lightweight professional code editor for Unity and code files
Exec=${EXEC_PATH}
Terminal=false
Categories=Development;Utility;
MimeType=text/plain;text/x-python;text/x-csrc;text/x-csharp;text/x-c++src;text/javascript;text/html;text/css;application/json;
EOF

if [[ -f "$ICON_PATH" ]]; then
  echo "Icon=${ICON_PATH}" >> "$DESKTOP_FILE"
fi

update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true

mimes=(
  text/plain
  text/x-python
  text/x-csrc
  text/x-csharp
  text/x-c++src
  text/javascript
  text/html
  text/css
  application/json
)

for m in "${mimes[@]}"; do
  xdg-mime default "$DESKTOP_ID" "$m" || true
done

echo "Installed desktop entry: $DESKTOP_FILE"
echo "Set ${APP_NAME} as default for common code/text mime types."