import React, { useState } from 'react';
import axios from 'axios';
import { Upload, Sun, Sparkles, Loader2, Download, Image as ImageIcon } from 'lucide-react';

// Your specific Hugging Face Space URL
const API_URL = "https://pramanikkunal65-low-light-enhancer.hf.space/enhance";

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  // Handle file selection and local preview
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
      setPreview(URL.createObjectURL(file));
      setResult(null); // Clear previous result
    }
  };

  // Communicate with the Hugging Face Python Backend [cite: 12, 14, 21]
  const processImage = async () => {
    if (!selectedFile) return;
    setLoading(true);
    
    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await axios.post(API_URL, formData, {
        responseType: 'blob', // Important for handling image data
      });
      const outputUrl = URL.createObjectURL(response.data);
      setResult(outputUrl);
    } catch (err) {
      console.error("Error:", err);
      alert("Failed to process image. Ensure the Hugging Face Space is 'Running'.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0f172a] text-slate-200 font-sans p-4 md:p-10">
      {/* Header Section */}
      <div className="max-w-6xl mx-auto text-center mb-12">
        <h1 className="text-4xl md:text-6xl font-extrabold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent mb-4">
          IllumiRefine AI
        </h1>
        <p className="text-slate-400 text-lg md:text-xl max-w-2xl mx-auto">
          Advanced Low-Light Enhancement using Homomorphic Filtering and Illumination-Reflectance Separation.
        </p>
      </div>

      {/* Main Interaction Area */}
      <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-10">
        
        {/* Left Column: Input */}
        <div className="flex flex-col gap-6">
          <div className="bg-slate-800/40 border border-slate-700 rounded-3xl p-6 shadow-xl">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2 text-blue-400">
              <Upload size={20}/> 1. Upload Low-Light Image
            </h2>
            
            <div className="relative group aspect-video md:aspect-square bg-slate-900 rounded-2xl border-2 border-dashed border-slate-600 hover:border-blue-500 transition-colors flex items-center justify-center overflow-hidden">
              {preview ? (
                <img src={preview} alt="Preview" className="w-full h-full object-contain" />
              ) : (
                <div className="text-center p-10">
                  <ImageIcon className="mx-auto mb-4 text-slate-600" size={48} />
                  <p className="text-slate-500">Click to browse or drag and drop</p>
                </div>
              )}
              <input 
                type="file" 
                onChange={handleFileChange} 
                className="absolute inset-0 opacity-0 cursor-pointer" 
                accept="image/*"
              />
            </div>

            <button 
              onClick={processImage}
              disabled={!selectedFile || loading}
              className="w-full mt-6 py-4 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-700 disabled:cursor-not-allowed rounded-2xl font-bold text-white shadow-lg shadow-blue-900/20 transition-all flex items-center justify-center gap-2"
            >
              {loading ? <Loader2 className="animate-spin" /> : <Sparkles size={20} />}
              {loading ? "Applying Homomorphic Filter..." : "Enhance Image"}
            </button>
          </div>
        </div>

        {/* Right Column: Result */}
        <div className="flex flex-col gap-6">
          <div className="bg-slate-800/40 border border-slate-700 rounded-3xl p-6 shadow-xl">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2 text-emerald-400">
              <Sun size={20}/> 2. Enhanced Result
            </h2>
            
            <div className="aspect-video md:aspect-square bg-slate-900 rounded-2xl border border-slate-700 flex items-center justify-center overflow-hidden relative">
              {result ? (
                <img src={result} alt="Result" className="w-full h-full object-contain animate-in fade-in duration-700" />
              ) : (
                <div className="text-center">
                  {loading ? (
                    <div className="flex flex-col items-center gap-3">
                      <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                      <p className="text-blue-400 font-medium animate-pulse">Processing Fourier Transform...</p>
                    </div>
                  ) : (
                    <p className="text-slate-600 italic">Enhanced output will appear here after processing</p>
                  )}
                </div>
              )}
            </div>

            {result && (
              <a 
                href={result} 
                download="enhanced_image.png" 
                className="w-full mt-6 py-4 bg-emerald-600 hover:bg-emerald-500 text-white text-center rounded-2xl font-bold shadow-lg shadow-emerald-900/20 transition-all flex items-center justify-center gap-2"
              >
                <Download size={20} /> Download Result
              </a>
            )}
          </div>
        </div>

      </div>

      {/* Footer / Methodology Note */}
      <footer className="max-w-6xl mx-auto mt-12 text-center text-slate-500 text-sm border-t border-slate-800 pt-8">
        <p>Built for Advanced Image Processing (IT507) [cite: 1]</p>
        <p className="mt-2 text-slate-600">
          Methodology: Log Transform → FFT → Gaussian High-Pass Filter → IFFT → CLAHE → Denoising [cite: 15-23, 24-32]
        </p>
      </footer>
    </div>
  );
}

export default App;