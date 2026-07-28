# 🌟 IllumiRefine AI

**A Hybrid Architecture Combining Self-Calibrated Illumination and Adaptive Frequency Fusion for Extreme Low-Light Image Enhancement**

[![Live Demo](https://img.shields.io/badge/Live_Demo-Vercel-success?style=for-the-badge&logo=vercel)](https://illumi-refine-ai.vercel.app/)
[![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)]()
[![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)]()
[![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97_Hugging_Face-Spaces-yellow?style=for-the-badge)]()

Developed as an M.Sc. Data Science research project at **Dhirubhai Ambani University (DA-IICT)**.

---

## 📑 Table of Contents

1. [Project Overview](#-project-overview)
2. [Algorithmic Pipeline](#-algorithmic-pipeline)
   - [Phase 1 — Homomorphic Filtering](#phase-1--homomorphic-filtering)
   - [Phase 2 — Self-Calibrated Illumination (SCI)](#phase-2--self-calibrated-illumination-sci)
   - [Phase 3 — SCI-Guided Adaptive Fusion (Novel Contribution)](#phase-3--sci-guided-adaptive-fusion-novel-contribution)
3. [System Architecture](#-system-architecture)
4. [Visual Results](#-visual-results)
5. [Installation & Local Setup](#-installation--local-setup)
6. [Cloud Deployment](#-cloud-deployment)
7. [Future Work](#-future-work)
8. [Contributors & Acknowledgments](#-contributors--acknowledgments)

---

## 🚀 Project Overview

**IllumiRefine AI** is a full-stack, end-to-end algorithmic framework designed to recover structural fidelity, maintain color constancy, and suppress heavy sensor noise in images captured under extreme low-light and High Dynamic Range (HDR) conditions.

The project moves from classical Fourier-domain mathematics to state-of-the-art unsupervised deep learning. The final deployed system pairs an ultra-lightweight Convolutional Neural Network (under 1 MB) with adaptive mathematical post-processing to deliver near real-time, professional-grade enhancement.

---

## 🧠 Algorithmic Pipeline

### Phase 1 — Homomorphic Filtering

The project began by modeling Retinex theory in the frequency domain. Applying a natural logarithm to the image transforms the multiplicative relationship between illumination and reflectance into an additive one. A **2D Fast Fourier Transform (FFT)** combined with a **Gaussian High-Pass Filter** then suppresses low-frequency shadows while preserving high-frequency edges.

### Phase 2 — Self-Calibrated Illumination (SCI)

To move beyond the limitations of static mathematical filters, the pipeline adopts the unsupervised deep learning **SCI framework (CVPR 2022)**.

- **Training:** Uses a cascaded learning process with a self-calibrated module, allowing the network to converge without paired ground-truth data.
- **Inference:** The deployed model drops the calibration module entirely, relying on a single block of three `3×3` convolutions. This gives an operational footprint of just **0.0619 GFLOPs** and inference under **2 seconds** on cloud CPUs.

### Phase 3 — SCI-Guided Adaptive Fusion *(Novel Contribution)*

Standard Retinex-based deep learning models tend to suffer from mid-tone dullness and severe noise amplification in near-black regions. To address this, a custom post-processing hybrid layer was engineered:

1. **Adaptive Exposure & Fractional Gamma** — The AI's predicted spatial illumination tensor is boosted via an exposure gain matrix and fractional power-law compression, safely lifting deep shadows without blowing out HDR highlights (e.g., digital clock displays).
2. **Illumination-Guided Denoising Mask** — A candidate image is generated using Fast Non-Local Means (NLM) denoising. The AI's illumination map is then used as an alpha-blend mask to fuse the two images mathematically: near-black regions draw from the denoised matrix, while naturally bright regions draw from the raw, sharp matrix.

---

## 🏗 System Architecture

The project uses a decoupled, microservice-based architecture for global scalability:

| Layer | Stack | Responsibility |
|---|---|---|
| **Frontend (Client)** | React.js, Tailwind CSS | Local state, file handling, blob encoding — deployed on **Vercel's Edge Network** |
| **Backend (API)** | FastAPI (Python 3.11) | Asynchronous POST requests, dynamic tensor allocation, HTTP byte streaming |
| **Inference Engine** | PyTorch, OpenCV | Converts multipart form data to `(N, C, H, W)` tensors, runs `torch.no_grad()` inference, applies the Adaptive Fusion math, re-encodes to PNG — deployed on **Hugging Face Spaces** |

---

## 📸 Visual Results

> **Note:** Add your actual images to a `docs/` or `assets/` folder in the repo and update the paths below.

| Input (Extreme Low-Light) | Output (Adaptive Fusion Enhanced) |
| :---: | :---: |
| <img src="docs/input_pool.png" width="400"/> | <img src="docs/output_pool.png" width="400"/> |
| *Original HDR scene — severe photon deprivation obscures the pool structure.* | *Enhanced result — noise is fully suppressed; the red digital clock stays crisp without overexposing.* |

---

## 💻 Installation & Local Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Kunal-Pramanik/IllumiRefine-AI.git
cd IllumiRefine-AI
```

### 2. Backend Setup (PyTorch & FastAPI)

Requires Python 3.11+.

```bash
cd backend

# Create a virtual environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# Install dependencies (CPU-optimized PyTorch)
pip install -r requirements.txt

# Start the local API
python main.py
```

The backend will be available at `http://localhost:8000`.

### 3. Frontend Setup (React)

Open a new terminal window.

```bash
cd frontend

# Install Node modules
npm install

# Start the development server
npm start
```

The UI will automatically open at `http://localhost:3000`.

> **Important:** To route the local frontend to your local backend, set `const API_URL = "http://localhost:8000/enhance";` in `App.js`.

---

## ☁️ Cloud Deployment

### Hugging Face (Backend)

1. Create a new Hugging Face Space (Docker / FastAPI).
2. Upload the backend contents.
3. Ensure `requirements.txt` includes `--extra-index-url https://download.pytorch.org/whl/cpu` to prevent CUDA memory overflows during the Docker build.
4. Upload the pre-trained weights to `weights/difficult.pt`.

### Vercel (Frontend)

1. Push the repository to GitHub.
2. Import the `frontend` directory into a new Vercel project.
3. Ensure `API_URL` in `App.js` points to your live Hugging Face Space URL before pushing to production.

---

## 🔮 Future Work

- **Real-Time Video Stream Enhancement** — Integrate temporal consistency loss functions and recurrent memory blocks (LSTMs) to prevent frame-flickering in security feeds.
- **Edge Computing** — Quantize 32-bit floating-point weights to 8-bit integers and convert the model to TensorFlow Lite for native smartphone/drone deployment.
- **Downstream Vision Integration** — Pipe enhanced tensors directly into YOLOv8 for dark-scene object detection and autonomous navigation.

---

## 🤝 Contributors & Acknowledgments

**Developers**
- Kunal Pramanik — M.Sc. Data Science, Dhirubhai Ambani University
- Chauhan Aman Satpal — M.Sc. Data Science, Dhirubhai Ambani University

**Academic Guide**
- Dr. Srimanta Mandal — Associate Professor, Dhirubhai Ambani University

Special thanks to the authors of the Self-Calibrated Illumination (CVPR 2022) framework for their open-source contribution to the computer vision community.
