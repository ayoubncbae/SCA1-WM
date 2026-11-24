"""Package only web01; preserve original project and omit credentials/caches."""
from pathlib import Path
import zipfile,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
EXCLUDE={'node_modules','.tools','.cache','.git','test-results','playwright-report','outputs','__pycache__'}
def main():
    name=ROOT/'SCA1_WM_WEB01_GITHUB_READY.zip';files=[]
    for p in ROOT.rglob('*'):
        if not p.is_file() or any(x in EXCLUDE for x in p.relative_to(ROOT).parts) or p.suffix in ['.zip','.log','.tsbuildinfo'] or p.name in ['.env','.env.local','GITHUB_PACKAGE_VERIFICATION.json']:continue
        files.append(p)
    with zipfile.ZipFile(name,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in files:z.write(p,str(p.relative_to(ROOT)))
    with zipfile.ZipFile(name) as z:
        assert z.testzip() is None
        assert all(not any(x in EXCLUDE for x in Path(n).parts) for n in z.namelist())
        assert 'package-lock.json' in z.namelist() and 'dist/index.html' in z.namelist()
    summary=dict(status='PASS',files=len(files),bytes=name.stat().st_size,sha256=hashlib.sha256(name.read_bytes()).hexdigest(),excluded=sorted(EXCLUDE))
    (ROOT/'docs/GITHUB_PACKAGE_VERIFICATION.json').write_text(json.dumps(summary,indent=2));print(str(name));print(json.dumps(summary))
if __name__=='__main__':main()
