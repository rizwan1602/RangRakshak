# 🎨 Defect Image Generation (DIG) Prompts

This document contains the prompt library used with NVIDIA DIG to generate synthetic paint defects.

## Defect Types

### 1. Orange Peel
- `A highly detailed close-up of a glossy painted {surface} exhibiting severe orange peel texture, uneven wavy surface, reflecting {lighting}.`
- `Macro photography of automotive paint with orange peel defect on {surface}, showing bumpy texture resembling an orange skin.`

### 2. Scratch
- `A deep clear-coat scratch on a {color} painted {surface}, showing exposed primer, sharp edges, under {lighting}.`
- `Multiple fine swirl scratches on a high-gloss {color} {surface}, visible under direct harsh {lighting}.`

### 3. Fish Eye
- `A distinct fish eye crater defect in fresh {color} paint on a {surface}, showing the substrate at the center of the crater.`
- `Several fish eye paint defects clustered on a {color} {surface}, surface tension pushing paint away from contamination spots.`

### 4. Dust Nib
- `A small hard dust nib trapped under the clear coat of a {color} painted {surface}, creating a tiny sharp bump.`
- `Macro shot of dirt inclusion (dust nib) in automotive paint on a {surface}, casting a micro-shadow under {lighting}.`

### 5. Run / Sag
- `A severe paint run (sag) defect on a vertical {color} painted {surface}, thick teardrop shaped accumulation of paint.`
- `Curtaining and sagging of wet {color} paint on a {surface}, showing uneven thickness and downward flow.`

### 6. Color Mismatch
- `A {surface} showing a distinct color mismatch, one half is a slightly different shade of {color} than the other half, blending error.`
- `Automotive panel showing poor color matching, {color} base coat appearing mottled and inconsistent under {lighting}.`

### 7. Blistering
- `Paint blistering defect on a {color} {surface}, small raised bubbles indicating trapped moisture beneath the surface.`
- `Micro-blistering on a painted {surface}, cluster of tiny bubbles in the clear coat.`

### 8. Pin Hole
- `Tiny pin hole defects in {color} paint on a {surface}, resembling microscopic needle pricks in the finish.`
- `Solvent pop pinholes on a clear coated {color} {surface}, tiny dark dots where solvent escaped.`

### 9. Overspray
- `Rough textured overspray defect on a {color} {surface}, dull finish with microscopic paint droplets sitting on top.`
- `Dry spray/overspray on the edge of a {color} {surface}, lacking gloss and appearing matte and textured.`

## Variables

### {surface}
- `car body panel`
- `flat metal sheet`
- `curved automotive bumper`
- `car door`
- `car hood`
- `fender`

### {color}
- `gloss white`
- `metallic black`
- `candy apple red`
- `metallic silver`
- `deep navy blue`

### {lighting}
- `harsh fluorescent factory lighting`
- `diffused softbox lighting`
- `direct single point LED inspection light`
- `natural ambient daylight`
