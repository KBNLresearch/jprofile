<?xml version="1.0"?>
<!--
   Schematron jpylyzer schema: verify if JP2 conforms to 
   KB's  profile for access copies (A.K.A. KB_ACCESS_LOSSY_01/01/2015)
   Johan van der Knijff, KB / National Library of the Netherlands , 13 October 2017.
   Additional checks for ICC profile and resolution 
-->
<s:schema xmlns:s="http://purl.oclc.org/dsdl/schematron">
<s:ns uri="http://openpreservation.org/ns/jpylyzer/v2/" prefix="j"/> 

<s:pattern>
    <s:title>KB access JP2 2015, generic (no colour/resolution requirements)</s:title>

    <!-- check that the file element exists -->
    <s:rule context="/">
        <s:assert test="j:file">no file element found</s:assert>
    </s:rule>

    <!-- top-level checks -->
    <s:rule context="/j:file">

        <!-- check that success value equals 'True' -->
        <s:assert test="j:statusInfo/j:success = 'True'">jpylyzer did not run successfully</s:assert>
         
        <!-- check that isValid element exists with the text 'True' -->
        <s:assert test="j:isValid = 'True'">not valid JP2</s:assert>
    </s:rule>

</s:pattern>
</s:schema>

