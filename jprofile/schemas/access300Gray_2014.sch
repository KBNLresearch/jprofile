<?xml version="1.0"?>
<!--
   Schematron jpylyzer schema: verify if JP2 conforms to 
   KB's  profile for access copies (A.K.A. KB_ACCESS_LOSSY_01/07/2014)
   Johan van der Knijff, KB / National Library of the Netherlands , 2 December 2014.
   Additional checks for ICC profile and resolution 
   
-->
<s:schema xmlns:s="http://purl.oclc.org/dsdl/schematron">
  <s:pattern>
    <s:title>KB master JP2 check</s:title>
    <!-- check that the jpylyzer element exists -->
    <s:rule context="/">
      <s:assert test="jpylyzer">no jpylyzer element found</s:assert>
    </s:rule>
    <!-- check that isValidJP2 element exists with the text 'True' -->
    <s:rule context="/jpylyzer">
      <s:assert test="isValidJP2 = 'True'">no valid JP2</s:assert>
    </s:rule>
    <!-- Top-level properties checks -->
    <s:rule context="/jpylyzer/properties">
      <!-- check that xml box exists -->
      <s:assert test="xmlBox">no XML box</s:assert>
      <!-- check if compression ratio doesn't exceed threshold value (a bit tricky as for images that 
         don't contain much information very high compression ratios may be obtained without losing quality)  
          -->
      <s:assert test="compressionRatio &lt; 25">compression ratio too high</s:assert>
    </s:rule>
    <!-- check that resolution box exists -->
    <s:rule context="/jpylyzer/properties/jp2HeaderBox">
      <s:assert test="resolutionBox">no resolution box</s:assert>
    </s:rule>
    <!-- check that resolution box contains capture resolution box -->
    <s:rule context="/jpylyzer/properties/jp2HeaderBox/resolutionBox">
      <s:assert test="captureResolutionBox">no capture resolution box</s:assert>
    </s:rule>
    <!-- check that resolution is correct value (tolerance of +/- 1 ppi to allow for rounding errors) -->
    <s:rule context="/jpylyzer/properties/jp2HeaderBox/resolutionBox/captureResolutionBox">
      <s:assert test="(vRescInPixelsPerInch &gt; 299) and (vRescInPixelsPerInch &lt; 301)">wrong vertical capture resolution </s:assert>
      <s:assert test="(hRescInPixelsPerInch &gt; 299) and (hRescInPixelsPerInch &lt; 301)">wrong horizontal capture resolution </s:assert>
    </s:rule>
    <!-- check that number of colour components equals 1 -->
    <s:rule context="/jpylyzer/properties/jp2HeaderBox/imageHeaderBox">
      <s:assert test="nC = '1'">wrong number of colour components</s:assert>
    </s:rule>
    <!-- check that METH equals 'Restricted ICC' -->
    <s:rule context="/jpylyzer/properties/jp2HeaderBox/colourSpecificationBox">
      <s:assert test="meth = 'Restricted ICC'">METH not 'Restricted ICC'</s:assert>
    </s:rule>
    <!-- check that ICC profile description equals 'Gray Gamma 2.2' -->
    <s:rule context="/jpylyzer/properties/jp2HeaderBox/colourSpecificationBox/icc">
      <s:assert test="description = 'Gray Gamma 2.2'">wrong colour space</s:assert>
    </s:rule>
    <!-- check X- and Y- tile sizes -->
    <s:rule context="/jpylyzer/properties/contiguousCodestreamBox/siz">
      <s:assert test="xTsiz = '1024'">wrong X Tile size</s:assert>
      <s:assert test="yTsiz = '1024'">wrong Y Tile size</s:assert>
    </s:rule>
    <!-- checks on codestream COD parameters -->
    <s:rule context="/jpylyzer/properties/contiguousCodestreamBox/cod">
      <!-- Error resilience features: sop, eph and segmentation symbols -->
      <s:assert test="sop = 'yes'">no start-of-packet headers</s:assert>
      <s:assert test="eph = 'yes'">no end-of-packet headers</s:assert>
      <s:assert test="segmentationSymbols = 'yes'">no segmentation symbols</s:assert>
      <!-- Progression order -->
      <s:assert test="order = 'RPCL'">wrong progression order</s:assert>
      <!-- Layers -->
      <s:assert test="layers = '8'">wrong number of layers</s:assert>
      <!-- Colour transformation (only for RGB images, i.e. number of components = 3)-->
      <s:assert test="(multipleComponentTransformation = 'yes') and (../../jp2HeaderBox/imageHeaderBox/nC = '3')                      or (multipleComponentTransformation = 'no') and (../../jp2HeaderBox/imageHeaderBox/nC = '1')">
                     no colour transformation</s:assert>
      <!-- Decomposition levels -->
      <s:assert test="levels = '5'">wrong number of decomposition levels</s:assert>
      <!-- Codeblock size -->
      <s:assert test="codeBlockWidth = '64'">wrong codeblock width</s:assert>
      <s:assert test="codeBlockHeight = '64'">wrong codeblock height</s:assert>
      <!-- Transformation (lossy vs lossless) -->
      <s:assert test="transformation = '9-7 irreversible'">wrong transformation</s:assert>
    </s:rule>
    <!-- Check specs reference as codestream comment (TODO: if file contains multiple codestream
            comments this may generate an error, might be possible to improve this -->
    <s:rule context="/jpylyzer/properties/contiguousCodestreamBox/com">
      <s:assert test="comment = 'KB_ACCESS_LOSSY_01/07/2014'">wrong codestream comment string</s:assert>
    </s:rule>
     </s:pattern>
</s:schema>
