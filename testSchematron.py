# Example adapted from http://lxml.de/validation.html#id2
import StringIO
from lxml import isoschematron
from lxml import etree

def main():
        
    # Schema
    f = StringIO.StringIO('''\
    <schema xmlns="http://purl.oclc.org/dsdl/schematron" >
    <pattern id="sum_equals_100_percent">
    <title>Sum equals 100%.</title>
    <rule context="Total">
    <assert test="sum(//Percent)=100">Sum is not 100%.</assert>
    </rule>
    </pattern>
    </schema>
    ''')

    # Parse schema
    sct_doc = etree.parse(f)
    schematron = isoschematron.Schematron(sct_doc, store_report = True)
    
    # XML to validate - validation will fail because sum of numbers not equal to 100 
    notValid = StringIO.StringIO('''\
        <Total>
        <Percent>30</Percent>
        <Percent>30</Percent>
        <Percent>50</Percent>
        </Total>
        ''')
    # Parse xml
    doc = etree.parse(notValid)
    
    # Validate against schema
    validationResult = schematron.validate(doc)
        
    # Validation report (assuming here this is where reason 
    # for validation failure is stored, but perhaps I'm wrong?)
    report = isoschematron.Schematron.validation_report
    
    print("is valid: " + str(validationResult))
    print(dir(report.__doc__))
    

main()


