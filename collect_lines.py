# -*- coding: utf-8 -*-
from pathlib import Path

root = Path(r"c:/Users/mon pc/Downloads/Mon CV et mon site/app")
app_lines = (root / "app.py").read_text(encoding="utf-8").splitlines()
with open(root / "line_info.txt", "w", encoding="utf-8") as fh:
    for idx, line in enumerate(app_lines, start=1):
        if "import base64" in line:
            fh.write(f"app/app.py:{idx}:import base64\n")
        if "photo_src = resolve_profile_photo" in line:
            fh.write(f"app/app.py:{idx}:photo src assignment\n")
        if "def resolve_profile_photo" in line:
            fh.write(f"app/app.py:{idx}:resolve helper start\n")

    admin_lines = (root / "pages" / "7_Admin.py").read_text(encoding="utf-8").splitlines()
    for idx, line in enumerate(admin_lines, start=1):
        if "with st.form(\"profile-form\")" in line:
            fh.write(f"app/pages/7_Admin.py:{idx}:profile form start\n")
        if "if not submitted:" in line:
            fh.write(f"app/pages/7_Admin.py:{idx}:guard return\n")
        if "updated_profile = {" in line:
            fh.write(f"app/pages/7_Admin.py:{idx}:profile dict creation\n")
        if "photo_bytes = photo.getvalue()" in line:
            fh.write(f"app/pages/7_Admin.py:{idx}:capture upload bytes\n")
        if 'updated_profile["photo"] = f"uploads/{filename}"' in line:
            fh.write(f"app/pages/7_Admin.py:{idx}:store uploads path\n")
