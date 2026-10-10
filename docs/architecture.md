# 🏗️ Architecture: RangRakshak

This document outlines the detailed architecture of the RangRakshak AI-powered paint quality inspection system, leveraging the NVIDIA Physical AI stack.

## 1. System Overview

RangRakshak is designed to completely eliminate the need for real-world defect data collection by heavily utilizing synthetic data generation. The system consists of three main pipelines:
1. **Synthetic Data Generation Pipeline**
2. **Model Training & Validation Pipeline**
3. **Deployment & Robotics Integration Pipeline**

## 2. Data Flow Diagram

```mermaid
flowchart TD
    subgraph Data Generation
        C1[Cosmos World Models] -->|Lighting/Env Conditions| D1[DIG (Defect Image Generation)]
        P1[Prompt Library] --> D1
        D1 -->|Raw Synthetic Images| V1[Video Data Augmentation]
        V1 -->|Augmented Dataset| S1[(Synthetic Dataset Storage)]
    end

    subgraph Training & Validation
        S1 --> T1[Vision Model Training]
        T1 -->|Trained Weights| I1[Isaac Sim Validation]
        I1 -->|Performance Metrics| T1
        I1 -->|Verified Model| M1[(Model Registry)]
    end

    subgraph Deployment
        M1 --> E1[TensorRT Optimization]
        E1 --> J1[Jetson Orin (Edge)]
        J1 -->|Inference| R1[Trakr + NemoClaw]
        I2[Isaac Lab RL Policy] --> R1
    end
```

## 3. NVIDIA Component Descriptions

- **NVIDIA DIG (Defect Image Generation)**: The core engine for generating physically accurate defects (orange peel, scratches, etc.) on varying surfaces and colors.
- **NVIDIA Cosmos World Foundation Models**: Used to generate realistic factory environments, simulating varying lighting conditions, reflections, and shadows to make the synthetic data robust against real-world domain shifts.
- **NVIDIA Video Data Augmentation (VDA)**: Synthesizes temporal variations simulating a moving camera across a painted surface, which is critical for video-based inference.
- **Isaac Sim**: Provides a high-fidelity 3D digital twin of the inspection environment. Used for closed-loop validation of the vision model before real-world deployment.
- **Isaac Lab & IsaacLabArena**: Used for training Reinforcement Learning (RL) policies for the Trakr quadruped and NemoClaw, optimizing camera positioning to minimize glare and maximize defect visibility.
- **Trakr & NemoClaw**: The physical embodiment of the inspection agent.

## 4. Integration Points

- **Cosmos to DIG**: Cosmos generates the base HDRI/environment maps which DIG uses for accurate reflection rendering on painted surfaces.
- **DIG to VDA**: Static images from DIG are passed to VDA to create synthetic video clips, adding motion blur and lighting shifts.
- **Trained Model to Isaac Sim**: The PyTorch/TensorRT model is loaded into Isaac Sim via ROS2 or Omniverse extensions to run inference on simulated camera feeds.

## 5. Deployment Architecture

The system is designed for cloud-native training and edge-native inference.
- **Cloud/Training**: Brev Launchables (H200 GPU) for massive parallel generation using DIG/Cosmos and rapid model training.
- **Edge/Inference**: NVIDIA Jetson AGX Orin deployed on the factory floor, directly interfaced with the robot's camera and control systems.

## 6. Edge Deployment Path (Jetson Orin for Factory)

1. Export the trained PyTorch model to ONNX.
2. Compile ONNX to a highly optimized TensorRT engine on the target Jetson Orin.
3. Deploy the inference node as a containerized ROS2 package.
4. Integrate with Trakr's navigation stack to trigger inference at designated inspection waypoints.
