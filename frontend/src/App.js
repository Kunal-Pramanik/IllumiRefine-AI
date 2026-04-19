import React, { useState } from 'react';
import axios from 'axios';
import { Upload, Sun, Sparkles, Loader2, Download, Image as ImageIcon, Github, Linkedin } from 'lucide-react';

const API_URL = "https://pramanikkunal65-low-light-enhancer.hf.space/enhance";

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
      setPreview(URL.createObjectURL(file));
      setResult(null); 
    }
  };

  const processImage = async () => {
    if (!selectedFile) return;
    setLoading(true);
    const formData = new FormData();
    formData.append('file', selectedFile);
    try {
      const response = await axios.post(API_URL, formData, { responseType: 'blob' });
      setResult(URL.createObjectURL(response.data));
    } catch (err) {
      alert("Error: Ensure backend is running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0f172a] text-slate-200 font-sans p-4 md:px-10 md:py-6">
      
      {/* Top Header & Navbar */}
      <header className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center mb-8 gap-4 border-b border-slate-800 pb-6">
        <div className="text-center md:text-left">
          <h1 className="text-3xl md:text-4xl font-black bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
            IllumiRefine AI
          </h1>
          <p className="text-slate-500 text-xs md:text-sm font-medium mt-1">
            Homomorphic Filtering & Illumination Separation
          </p>
        </div>

        {/* Branding & Links - Top Right */}
        <div className="flex flex-col items-center md:items-end gap-2">
          <a 
            href="https://www.linkedin.com/in/kunal-pramanik-5aa131267" 
            target="_blank" rel="noopener noreferrer"
            className="group flex items-center gap-2"
          >
            <span className="text-slate-500 text-[10px] uppercase tracking-widest font-bold group-hover:text-blue-400">Developed by</span>
            <span className="text-lg font-bold text-white group-hover:text-blue-400 transition-colors flex items-center gap-1">
              Kunal Pramanik <Linkedin size={14} className="text-blue-500" />
            </span>
          </a>
          <a 
            href="https://github.com/Kunal-Pramanik/IllumiRefine-AI.git" 
            target="_blank" rel="noopener noreferrer"
            className="flex items-center gap-2 px-4 py-1.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-full text-[11px] font-bold text-slate-300 transition-all shadow-lg shadow-black/20"
          >
            <Github size={14} /> Project Details
          </a>
        </div>
      </header>

      {/* Main Content - Compact Grid */}
      <main className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
        
        {/* Input Box */}
        <div className="bg-slate-800/30 border border-slate-700/50 rounded-2xl p-4 md:p-5">
          <h2 className="text-sm font-bold mb-3 flex items-center gap-2 text-blue-400 uppercase tracking-wider">
            <Upload size={16}/> 1. Input
          </h2>
          <div className="relative aspect-[4/3] bg-slate-900 rounded-xl border-2 border-dashed border-slate-700 hover:border-blue-500 transition-colors overflow-hidden">
            {preview ? (
              <img src={preview} alt="Preview" className="w-full h-full object-contain" />
            ) : (
              <div className="h-full flex flex-col items-center justify-center text-slate-600">
                <ImageIcon size={40} className="mb-2 opacity-20" />
                <p className="text-xs">Drop image here</p>
              </div>
            )}
            <input type="file" onChange={handleFileChange} className="absolute inset-0 opacity-0 cursor-pointer" accept="image/*" />
          </div>
          <button 
            onClick={processImage}
            disabled={!selectedFile || loading}
            className="w-full mt-4 py-3 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-700 rounded-xl font-bold text-sm transition-all flex items-center justify-center gap-2"
          >
            {loading ? <Loader2 size={18} className="animate-spin" /> : <Sparkles size={18} />}
            {loading ? "Enhancing..." : "Enhance Image"}
          </button>
        </div>

        {/* Output Box */}
        <div className="bg-slate-800/30 border border-slate-700/50 rounded-2xl p-4 md:p-5">
          <h2 className="text-sm font-bold mb-3 flex items-center gap-2 text-emerald-400 uppercase tracking-wider">
            <Sun size={16}/> 2. Result
          </h2>
          <div className="aspect-[4/3] bg-slate-900 rounded-xl border border-slate-700 flex items-center justify-center overflow-hidden">
            {result ? (
              <img src={result} alt="Result" className="w-full h-full object-contain" />
            ) : (
              <p className="text-slate-700 text-xs italic">{loading ? "Filtering frequencies..." : "Awaiting input..."}</p>
            )}
          </div>
          {result && (
            <a href={result} download="enhanced.png" className="w-full mt-4 py-3 bg-emerald-600/90 hover:bg-emerald-500 rounded-xl font-bold text-sm text-center flex items-center justify-center gap-2">
              <Download size={18} /> Download
            </a>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
