# Tesseract Performance Testing

This is a small framework for testing various approaches to using Tesseract so that the best-performing approach can be found. There are a lot of people using Tesseract, but very little research being done (at least publicly) around how to make it faster. 

The research I do here is with a version of Tesseract that is trained to do well on legal fonts, [as described on my blog][tess].

# Approaches Tested

The assumption is that we start with a PDF containing scanned images and we want to perform OCR on it. The tests performed are:

 - Analyze whether it's the image conversion or the OCR that takes so much time.
   
 - Can images can be held in memory rather than written to disk and then pulled from disk?

 - Converting to grayscale using something like `mogrify -type Grayscale *.tif`

 - Using TIFFs, PNGs or JPEGs
 
 - Using lower/higher DPI
 
 - Different libraries


# Results

 - Lower density is faster for image conversion. 150 is about twice as fast as 300, however lower density takes longer for OCR. This means that higher density is best since it provides better quality.
 
 - Keeping images completely in memory saves time and should be done by piping images into Tesseract (this is only supported in version 3.04 of tesseract or later).
 
 - Most time is spent doing OCR, not converting images. There's not much we can do to improve this.
 
 - Initializing Tesseract accounts for very little of the time. This was proven by comparing the conversion of one multi-page tiff to converting the same tiff images as separate tiffs (thus initializing Tesseract once/page).

 - Converting to grayscale does not affect performance.
 
 - Switching to multi-page tiffs did cause one crash, so I'm hesitant to use them. 
 

[tess]: http://michaeljaylissner.com/posts/2012/02/11/adding-new-fonts-to-tesseract-3-ocr-engine/
