import React, { useEffect } from 'react';

interface SecurityModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const SecurityModal: React.FC<SecurityModalProps> = ({ isOpen, onClose }) => {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 bg-black/80 backdrop-blur-sm z-[100] flex items-center justify-center p-4 animate-in fade-in duration-200"
      onClick={onClose}
    >
      <div
        className="bg-slate-900 border border-gold/60 rounded-2xl max-w-2xl w-full p-6 sm:p-7 shadow-2xl space-y-5 max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex justify-between items-start border-b border-slate-800 pb-4">
          <div className="flex items-center gap-3">
            <span className="text-3xl p-2 rounded-xl bg-gold/10 border border-gold/30">🛡️</span>
            <div>
              <h3 className="text-lg sm:text-xl font-bold text-gold-soft">
                Privacy & Security Guarantee
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                How Project Quarm Chronicle protects your files and game installation
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white text-xl p-1 leading-none transition-colors"
            title="Close"
          >
            &times;
          </button>
        </div>

        {/* Security Points */}
        <div className="space-y-4 text-xs sm:text-sm text-slate-300">
          {/* Point 1: Read-Only */}
          <div className="flex items-start gap-3 p-3.5 rounded-xl bg-slate-950/60 border border-slate-800">
            <span className="text-xl">🔒</span>
            <div>
              <h4 className="font-bold text-slate-100 mb-1">
                Browser-Enforced Read-Only Access
              </h4>
              <p className="text-xs text-slate-400 leading-relaxed">
                When you connect your TAKP directory, the browser requests strictly <strong className="text-emerald-400">read-only</strong> permission (<code className="text-cyan bg-slate-900 px-1 py-0.5 rounded">mode: 'read'</code>). The browser engine physically prevents modifying, deleting, renaming, or saving files. Any write attempt is blocked at the operating system sandbox level and triggers a browser security error.
              </p>
            </div>
          </div>

          {/* Point 2: Sandboxed Web Environment */}
          <div className="flex items-start gap-3 p-3.5 rounded-xl bg-slate-950/60 border border-slate-800">
            <span className="text-xl">🧱</span>
            <div>
              <h4 className="font-bold text-slate-100 mb-1">
                Sandboxed Web Environment
              </h4>
              <p className="text-xs text-slate-400 leading-relaxed">
                Web browsers run web applications inside an isolated sandbox. Web pages have <strong className="text-slate-200">zero ability</strong> to execute binary files (<code className="text-slate-300">.exe</code>), inject dynamic libraries (<code className="text-slate-300">.dll</code>), or touch any running game processes. Your EverQuest client and system executables cannot be modified or run by this application.
              </p>
            </div>
          </div>

          {/* Point 3: 100% Client-Side */}
          <div className="flex items-start gap-3 p-3.5 rounded-xl bg-slate-950/60 border border-slate-800">
            <span className="text-xl">💻</span>
            <div>
              <h4 className="font-bold text-slate-100 mb-1">
                100% Client-Side (Zero Server Uploads)
              </h4>
              <p className="text-xs text-slate-400 leading-relaxed">
                All parsing is performed locally on your device inside a local Web Worker thread. Your log files and character chronicles are never transmitted to any external server or third party. You can disconnect your internet while parsing and it will work completely offline.
              </p>
            </div>
          </div>

          {/* Point 4: Zero-Folder Option */}
          <div className="flex items-start gap-3 p-3.5 rounded-xl bg-slate-950/60 border border-slate-800">
            <span className="text-xl">📄</span>
            <div>
              <h4 className="font-bold text-slate-100 mb-1">
                No Folder Access Required
              </h4>
              <p className="text-xs text-slate-400 leading-relaxed">
                If you prefer not to grant folder-level access, you do not have to. Click <strong className="text-cyan">"Select eqlog_*.txt Files"</strong> or drag and drop your log files directly. This uses the standard HTML file picker, giving the browser temporary read access only to the exact text files you select.
              </p>
            </div>
          </div>
        </div>

        {/* Documentation Link */}
        <div className="bg-slate-950/90 border border-cyan/30 rounded-xl p-3.5 flex items-center justify-between gap-3">
          <div className="text-xs text-slate-300">
            <span className="font-semibold text-cyan">Want independent technical verification?</span>
            <p className="text-[11px] text-slate-400 mt-0.5">
              Read Mozilla's neutral technical documentation on File System Access API security guarantees.
            </p>
          </div>
          <a
            href="https://developer.mozilla.org/en-US/docs/Web/API/File_System_Access_API#security_considerations"
            target="_blank"
            rel="noopener noreferrer"
            className="px-3 py-1.5 rounded-lg bg-cyan/15 border border-cyan/50 text-cyan hover:bg-cyan/25 text-xs font-semibold whitespace-nowrap transition-colors flex items-center gap-1 shrink-0"
          >
            <span>MDN Web Docs</span>
            <span>&rarr;</span>
          </a>
        </div>

        {/* Footer */}
        <div className="flex justify-between items-center pt-3 border-t border-slate-800">
          <span className="text-[11px] text-slate-500">
            Permissions can be revoked at any time via browser site settings.
          </span>
          <button
            type="button"
            onClick={onClose}
            className="px-5 py-2 rounded-lg bg-gold/20 border border-gold text-gold-soft hover:bg-gold/30 font-bold text-xs transition-all shadow-gold-glow"
          >
            Understood
          </button>
        </div>
      </div>
    </div>
  );
};
