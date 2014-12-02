<?xml version="1.0"?>
<!--
   Schematron jpylyzer schema: verify if JP2 conforms to 
   KB's  profile for access copies (A.K.A. KB_ACCESS_LOSSY_30/03/2011)
   Johan van der Knijff, KB / National Library of the Netherlands , 16 August 2012.
   Based on original schema by Adam Retter, The National Archives

TO DO: 
 
1. Better handling of multiple codestream comment instances
2. Perhaps drop check of compression ratio
   
-->
<s:schema xmlns:s="http://purl.oclc.org/dsdl/schematron">
  <s:pattern>
    <s:title>KB access JP2 check</s:title>
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
      <!-- check if XML box exists -->
      <s:assert test="xmlBox">no XML box</s:assert>
      <!-- check if compression ratio doesn't exceed threshold value (a bit tricky as for images that 
         don't contain much information very high compression ratios may be obtained without losing quality)  
          -->
      <s:assert test="compressionRatio &lt; 25">compression ratio too high</s:assert>
    </s:rule>
    <!-- check if resolution box exists -->
    <s:rule context="/jpylyzer/properties/jp2HeaderBox">
      <s:assert test="resolutionBox">no resolution box</s:assert>
    </s:rule>
    <!-- check if resolution box contains capture resolution box -->
    <s:rule context="/jpylyzer/properties/jp2HeaderBox/resolutionBox">
      <s:assert test="captureResolutionBox">no capture resolution box</s:assert>
    </s:rule>
    <!-- check that resolution is correct value (tolerance of +/- 1 ppi to allow for rounding errors) -->
    <s:rule context="/jpylyzer/properties/jp2HeaderBox/resolutionBox/captureResolutionBox">
      <s:assert test="(vRescInPixelsPerInch &gt; 149) and (vRescInPixelsPerInch &lt; 151)">wrong vertical capture resolution </s:assert>
      <s:assert test="(hRescInPixelsPerInch &gt; 149) and (hRescInPixelsPerInch &lt; 151)">wrong horizontal capture resolution </s:assert>
    </s:rule>
    <!-- check that METH equals 'Restricted ICC' -->
    <s:rule context="/jpylyzer/properties/jp2HeaderBox/colourSpecificationBox">
      <s:assert test="meth = 'Restricted ICC'">METH not 'Restricted ICC'</s:assert>
    </s:rule>
    <!-- check that ICC profile description equals 'Adobe RGB (1998)' -->
    <s:rule context="/jpylyzer/properties/jp2HeaderBox/colourSpecificationBox/icc">
      <s:assert test="description = 'Adobe RGB (1998)'">wrong colour space</s:assert>
    </s:rule>
    <!-- check X- and Y- tile sizes -->
    <s:rule context="/jpylyzer/properties/contiguousCodestreamBox/siz">
      <s:assert test="xTsiz = '1024'">wrong X Tile size</s:assert>
      <s:assert test="yTsiz = '1024'">wrong Y Tile size</s:assert>
    </s:rule>
    <!-- checks on codestream COD parameters -->
    <s:rule context="/jpylyzer/properties/contiguousCodestreamBox/cod">
      <!-- Precincts -->
      <s:assert test="precincts = 'yes'">no precincts</s:assert>
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
      <!-- checks on X- and Y- precinct sizes: 256x256 for 2 highest resolution levels,
              128x128 for remaining ones  -->
      <s:assert test="precinctSizeX[1] = '128'">precinctSizeX doesn't match profile</s:assert>
      <s:assert test="precinctSizeX[2] = '128'">precinctSizeX doesn't match profile</s:assert>
      <s:assert test="precinctSizeX[3] = '128'">precinctSizeX doesn't match profile</s:assert>
      <s:assert test="precinctSizeX[4] = '128'">precinctSizeX doesn't match profile</s:assert>
      <s:assert test="precinctSizeX[5] = '256'">precinctSizeX doesn't match profile</s:assert>
      <s:assert test="precinctSizeX[6] = '256'">precinctSizeX doesn't match profile</s:assert>
      <s:assert test="precinctSizeY[1] = '128'">precinctSizeY doesn't match profile</s:assert>
      <s:assert test="precinctSizeY[2] = '128'">precinctSizeY doesn't match profile</s:assert>
      <s:assert test="precinctSizeY[3] = '128'">precinctSizeY doesn't match profile</s:assert>
      <s:assert test="precinctSizeY[4] = '128'">precinctSizeY doesn't match profile</s:assert>
      <s:assert test="precinctSizeY[5] = '256'">precinctSizeY doesn't match profile</s:assert>
      <s:assert test="precinctSizeY[6] = '256'">precinctSizeY doesn't match profile</s:assert>
    </s:rule>
    <!-- Check specs reference as codestream comment (TODO: if file contains multiple codestream
            comments this may generate an error, might be possible to improve this -->
    <s:rule context="/jpylyzer/properties/contiguousCodestreamBox/com">
      <s:assert test="comment = 'KB_ACCESS_LOSSY_30/03/2011'">wrong codestream comment string</s:assert>
    </s:rule>
  </s:pattern>
</s:schema>
