import React, { useEffect, useMemo, useState } from 'react';
import { FileEntry } from '../../electron/preload';
import Editor from '@monaco-editor/react';

export default function App() {
  const [currentPath, setCurrentPath] = useState<string>(process.env.HOME || 'C:/');
  const [items, setItems] = useState<FileEntry[]>([]);
  const [selected, setSelected] = useState<FileEntry[]>([]);
  const [status, setStatus] = useState<string>('Ready');

  useEffect(() => {
    (async () => {
      try {
        if (currentPath.toLowerCase().endsWith('.zip')) {
          const list = await window.api.zipList(currentPath, '');
          setItems(list);
        } else {
          const list = await window.api.list(currentPath);
          setItems(list);
        }
        setStatus('Ready');
      } catch (e: any) {
        setStatus(e?.message || 'Error');
      }
    })();
  }, [currentPath]);

  async function openFolder() {
    const f = await window.api.openFolder();
    if (f) setCurrentPath(f);
  }

  async function openItem(it: FileEntry) {
    if (it.isDirectory) {
      setCurrentPath(it.fullPath);
    } else if (it.fullPath.toLowerCase().endsWith('.zip')) {
      setCurrentPath(it.fullPath);
    } else if (it.fullPath) {
      // For now just start drag; future: open editor tab
      await window.api.startDrag([it.fullPath]);
    }
  }

  async function copyHere() {
    const files = selected.map(s => s.fullPath);
    if (files.length === 0) return;
    await window.api.copy(files, currentPath);
    setStatus('Copied');
    setItems(await window.api.list(currentPath));
  }

  async function trashSelected() {
    const files = selected.map(s => s.fullPath);
    if (files.length === 0) return;
    await window.api.trash(files);
    setStatus('Deleted');
    setItems(await window.api.list(currentPath));
  }

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '260px 1fr 1fr', gridTemplateRows: 'auto 1fr auto', height: '100vh', background: '#1e1e1e', color: '#eee' }}>
      <div style={{ gridColumn: '1 / span 3', padding: 8, display: 'flex', gap: 8, alignItems: 'center', background: '#252526' }}>
        <button onClick={openFolder}>Open Folder</button>
        <input style={{ flex: 1 }} value={currentPath} onChange={e => setCurrentPath(e.target.value)} />
        <button onClick={() => setCurrentPath(currentPath)}>Refresh</button>
        <button onClick={copyHere}>Paste</button>
        <button onClick={trashSelected}>Delete</button>
      </div>

      <div style={{ padding: 8, borderRight: '1px solid #3c3c3c' }}>
        <b>Folders</b>
        <div style={{ opacity: 0.7 }}>Tree (coming soon)</div>
      </div>

      <div style={{ padding: 8, borderRight: '1px solid #3c3c3c' }}>
        <b>Files</b>
        <div style={{ marginTop: 8, height: 'calc(100% - 32px)', overflow: 'auto' }}
             onDrop={async (e) => {
               e.preventDefault();
               const files = Array.from(e.dataTransfer.files).map(f => f.path);
               if (files.length === 0) return;
               await window.api.copy(files, currentPath);
               setItems(await window.api.list(currentPath));
             }}
             onDragOver={(e) => e.preventDefault()}>
          {items.map(it => (
            <div key={it.fullPath} style={{ padding: '6px 8px', borderBottom: '1px solid #333', cursor: 'pointer', background: selected.includes(it) ? '#094771' : 'transparent' }}
                 onClick={(e) => {
                   if (e.ctrlKey) setSelected(prev => prev.includes(it) ? prev.filter(p => p !== it) : [...prev, it]);
                   else setSelected([it]);
                 }}
                 onDoubleClick={() => openItem(it)}
                 draggable
                 onDragStart={async (e) => { e.preventDefault(); await window.api.startDrag([it.fullPath]); }}>
              <div style={{ display: 'flex', gap: 12 }}>
                <div style={{ width: 240, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{it.name}</div>
                <div style={{ width: 100 }}>{it.isDirectory ? 'Folder' : 'File'}</div>
                <div style={{ width: 120 }}>{it.isDirectory ? '' : `${it.size} B`}</div>
                <div style={{ flex: 1 }}>{new Date(it.mtimeMs).toLocaleString()}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div style={{ padding: 8 }}>
        <b>Editor</b>
        <div style={{ marginTop: 8, height: 'calc(100% - 32px)' }}>
          <Editor theme="vs-dark" height="100%" defaultLanguage="plaintext" defaultValue={"// Open a file to edit"} />
        </div>
      </div>

      <div style={{ gridColumn: '1 / span 3', padding: 8, background: '#252526' }}>{status}</div>
    </div>
  );
}