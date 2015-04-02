<?xml version="1.0"?>
<!--
   Schematron jpylyzer schema: verify if JP2 conforms to 
   KB's  profile for access copies (A.K.A. KB_ACCESS_LOSSY_01/01/2015)
   Johan van der Knijff, KB / National Library of the Netherlands , 2 December 2014.
   
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
    <!-- check that METH equals 'Restricted ICC' -->
    <s:rule context="/jpylyzer/properties/jp2HeaderBox/colourSpecificationBox">
      <s:assert test="meth = 'Restricted ICC'">METH not 'Restricted ICC'</s:assert>
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
    <!-- Check specs reference as codestream comment -->
    <!-- Rule looks for one exact match, additional codestream comments are permitted -->
     <s:rule context="/jpylyzer/properties/contiguousCodestreamBox">
        <s:assert test="count(com/comment[text()='KB_ACCESS_LOSSY_01/01/2015']) =1">Expected codestream comment string missing</s:assert>
    </s:rule>
     </s:pattern>
</s:schema>
