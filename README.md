# Tesseract Performance Testing

This is a small framework for testing various approaches to using Tesseract so that the best-performing approach can be found. There are a lot of people using Tesseract, but very little research being done (at least publicly) around how to make it faster. 

The research I do here is with a version of Tesseract that is trained to do well on legal fonts, [as described on my blog][tess].

# Approaches Tested

The assumption is that we start with a PDF containing scanned images and we want to perform OCR on it. The tests performed are:

 - Analyze whether it's the image conversion or the OCR that takes so much time.
   - Tesseract takes more time on the CPU, image conversion takes more time in IO. Images account for about 30% of wall time, and Tesseract accounts for about 70% of wall time.
   
 - Can images can be held in memory rather than written to disk and then pulled from disk?

 - Converting to grayscale using something like `mogrify -type Grayscale *.tif`
    - This appears to make no difference in performance.
    - TODO: Does this improve quality?

 - Using TIFFs, PNGs or JPEGs
    - I'm hesitant to test this. In the past png was the most robust format.
 
 - Using lower/higher DPI
    - This fixes the IO problem somewhat while doing image conversion, but the Tesseract speed is similar.
 
 - Different libraries

# Results

 - Lower density is faster for image conversion. 150 is about twice as fast as 300.



[tess]: http://michaeljaylissner.com/posts/2012/02/11/adding-new-fonts-to-tesseract-3-ocr-engine/
