<?xml version="1.0"?>
<!--
   Schematron jpylyzer schema: verify if JP2 conforms to 
   KB's  profile for access copies (A.K.A. KB_ACCESS_LOSSY_01/01/2015)
   Johan van der Knijff, KB / National Library of the Netherlands , 13 October 2017.
   Additional checks for ICC profile and resolution 
-->
<s:schema xmlns:s="http://purl.oclc.org/dsdl/schematron">
<s:ns uri="http://openpreservation.org/ns/jpylyzer/" prefix="j"/> 

<s:pattern>
    <s:title>KB master JP2 2015, colour, 600 PPI</s:title>

    <!-- check that the jpylyzer element exists -->
    <s:rule context="/">
        <s:assert test="j:jpylyzer">no jpylyzer element found</s:assert>
    </s:rule>

    <!-- top-level Jpylyzer checks -->
    <s:rule context="/j:jpylyzer">

        <!-- check that success value equals 'True' -->
        <s:assert test="j:statusInfo/j:success = 'True'">jpylyzer did not run successfully</s:assert>
         
        <!-- check that isValidJP2 element exists with the text 'True' -->
        <s:assert test="j:isValidJP2 = 'True'">not valid JP2</s:assert>
    </s:rule>

    <!-- Top-level properties checks -->
    <s:rule context="/j:jpylyzer/j:properties">

        <!-- check that xml box exists -->
        <s:assert test="j:xmlBox">no XML box</s:assert>
    
    </s:rule>

    <!-- check that resolution box exists -->
    <s:rule context="/j:jpylyzer/j:properties/j:jp2HeaderBox">
        <s:assert test="j:resolutionBox">no resolution box</s:assert>
    </s:rule>

    <!-- check that resolution box contains capture resolution box -->
    <s:rule context="/j:jpylyzer/j:properties/j:jp2HeaderBox/j:resolutionBox">
        <s:assert test="j:captureResolutionBox">no capture resolution box</s:assert>
    </s:rule>

    <!-- check that resolution is correct value (tolerance of +/- 1 ppi to allow for rounding errors) -->
    <s:rule context="/j:jpylyzer/j:properties/j:jp2HeaderBox/j:resolutionBox/j:captureResolutionBox">
        <s:assert test="(j:vRescInPixelsPerInch &gt; 599) and
        (j:vRescInPixelsPerInch &lt; 601)">wrong vertical capture resolution </s:assert>
        <s:assert test="(j:hRescInPixelsPerInch &gt; 599) and 
        (j:hRescInPixelsPerInch &lt; 601)">wrong horizontal capture resolution </s:assert>
    </s:rule>

    <!-- check that number of colour components equals 3 -->
    <s:rule context="/j:jpylyzer/j:properties/j:jp2HeaderBox/j:imageHeaderBox">
        <s:assert test="j:nC = '3'">wrong number of colour components</s:assert>
    </s:rule>

    <!-- check that METH equals 'Restricted ICC' -->
    <s:rule context="/j:jpylyzer/j:properties/j:jp2HeaderBox/j:colourSpecificationBox">
        <s:assert test="j:meth = 'Restricted ICC'">METH not 'Restricted ICC'</s:assert>
    </s:rule>

    <!-- check that ICC profile description equals 'Adobe RGB (1998)' -->
    <s:rule context="/j:jpylyzer/j:properties/j:jp2HeaderBox/j:colourSpecificationBox/j:icc">
        <s:assert test="j:description = 'Adobe RGB (1998)'">wrong colour space</s:assert>
    </s:rule>

    <!-- check X- and Y- tile sizes -->
    <s:rule context="/j:jpylyzer/j:properties/j:contiguousCodestreamBox/j:siz">
        <s:assert test="j:xTsiz = '1024'">wrong X Tile size</s:assert>
        <s:assert test="j:yTsiz = '1024'">wrong Y Tile size</s:assert>
    </s:rule>

    <!-- checks on codestream COD parameters -->

    <s:rule context="/j:jpylyzer/j:properties/j:contiguousCodestreamBox/j:cod">

        <!-- Error resilience features: sop, eph and segmentation symbols -->
        <s:assert test="j:sop = 'yes'">no start-of-packet headers</s:assert>
        <s:assert test="j:eph = 'yes'">no end-of-packet headers</s:assert>
        <s:assert test="j:segmentationSymbols = 'yes'">no segmentation symbols</s:assert>

        <!-- Progression order -->
        <s:assert test="j:order = 'RPCL'">wrong progression order</s:assert>

        <!-- Layers -->
        <s:assert test="j:layers = '11'">wrong number of layers</s:assert>

        <!-- Colour transformation (only for RGB images, i.e. number of components = 3)-->
        <s:assert test="(j:multipleComponentTransformation = 'yes') and
                        (../../j:jp2HeaderBox/j:imageHeaderBox/j:nC = '3') or
                        (j:multipleComponentTransformation = 'no') and
                        (../../j:jp2HeaderBox/j:imageHeaderBox/j:nC = '1')">no colour transformation</s:assert>

        <!-- Decomposition levels -->
        <s:assert test="j:levels = '5'">wrong number of decomposition levels</s:assert>

        <!-- Codeblock size -->
        <s:assert test="j:codeBlockWidth = '64'">wrong codeblock width</s:assert>
        <s:assert test="j:codeBlockHeight = '64'">wrong codeblock height</s:assert>

        <!-- Transformation (irreversible vs reversible) -->
        <s:assert test="j:transformation = '5-3 reversible'">wrong transformation</s:assert>

        <!-- checks on X- and Y- precinct sizes: 256x256 for 2 highest resolution levels,
              128x128 for remaining ones  -->
        <s:assert test="j:precinctSizeX[1] = '128'">precinctSizeX doesn't match profile</s:assert>
        <s:assert test="j:precinctSizeX[2] = '128'">precinctSizeX doesn't match profile</s:assert>
        <s:assert test="j:precinctSizeX[3] = '128'">precinctSizeX doesn't match profile</s:assert>
        <s:assert test="j:precinctSizeX[4] = '128'">precinctSizeX doesn't match profile</s:assert>
        <s:assert test="j:precinctSizeX[5] = '256'">precinctSizeX doesn't match profile</s:assert>
        <s:assert test="j:precinctSizeX[6] = '256'">precinctSizeX doesn't match profile</s:assert>
        <s:assert test="j:precinctSizeY[1] = '128'">precinctSizeY doesn't match profile</s:assert>
        <s:assert test="j:precinctSizeY[2] = '128'">precinctSizeY doesn't match profile</s:assert>
        <s:assert test="j:precinctSizeY[3] = '128'">precinctSizeY doesn't match profile</s:assert>
        <s:assert test="j:precinctSizeY[4] = '128'">precinctSizeY doesn't match profile</s:assert>
        <s:assert test="j:precinctSizeY[5] = '256'">precinctSizeY doesn't match profile</s:assert>
        <s:assert test="j:precinctSizeY[6] = '256'">precinctSizeY doesn't match profile</s:assert>

    </s:rule>

    <!-- Check specs reference as codestream comment -->
    <!-- Rule looks for one exact match, additional codestream comments are permitted -->
    <s:rule context="/j:jpylyzer/j:properties/j:contiguousCodestreamBox">
        <s:assert test="count(j:com/j:comment[text()='KB_MASTER_LOSSLESS_01/01/2015']) =1">Expected codestream comment string missing</s:assert>
      </s:rule>
</s:pattern>
</s:schema>

