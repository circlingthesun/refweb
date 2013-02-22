#!/usr/bin/python
from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.layout import LTAnon, LAParams, LTContainer, LTPage, LTText, LTTextBox, LTChar, LTImage, LTLine, LTTextLine, LTRect, LTFigure
from pdfminer.converter import PDFConverter
import re
import sys
import datetime

class TMConverter(PDFConverter):

    def __init__(self, rsrcmgr, outfp, codec='utf-8', pageno=1, laparams=None,
                 showpageno=False):
        PDFConverter.__init__(self, rsrcmgr, outfp, codec=codec, pageno=pageno, laparams=laparams)
        self.showpageno = showpageno
        self.strbuff = ""
        self.start_ref = ""
        self.start_ref_no = -1;
        self.ref_section_reached = False
        self.re_ref = re.compile(r'\[(\d*)\]$')
        self.re_refsection = re.compile(r'\s*references\s*$', re.I)
        self.last_item = None

        self.refs = {}

        return


    def receive_layout(self, ltpage):
            

        def process_buffer():
            #print self.strbuff[-20:]
            #
            # Check if reference section reached
            #
            if not self.ref_section_reached:
                res = self.re_refsection.search(self.strbuff[-20:])
                if res:
                    print "FOUND REFS"
                    self.strbuff = ""
                    self.ref_section_reached = True


        def render(item):
            if isinstance(item, LTChar):

                dist = 0


                #
                # Add spaces in stream
                #
                if self.last_item:
                    vdist = self.last_item.y1 - item.y0
                    hdist = item.x0 - self.last_item.x1
                    if hdist > item.width/8 or vdist > item.height*1.5:
                        self.strbuff += " " + str(self.pageno) + " "
                        process_buffer()


                #
                # add text
                #

                text = item.get_text().encode(self.codec, 'ignore')
                self.strbuff += text
                self.last_item = item
        
            if isinstance(item, LTContainer):
                for child in item:
                    render(child)
            
            if isinstance(item, LTFigure):
                for child in item:
                    render(child)

            
        render(ltpage)
        return


def process(infile):
    # Create a PDF parser object associated with the file object.
    parser = PDFParser(infile)
    # Create a PDF document object that stores the document structure.
    doc = PDFDocument()
    # Connect the parser and document objects.
    parser.set_document(doc)
    doc.set_parser(parser)
    # Supply the password for initialization.
    # (If no password is set, give an empty string.)
    doc.initialize('')
    # Check if the document allows text extraction. If not, abort.
    if not doc.is_extractable:
        raise PDFTextExtractionNotAllowed
    # Create a PDF resource manager object that stores shared resources.
    rsrcmgr = PDFResourceManager()
    # Create a PDF page aggregator object.
    
    device = TMConverter(rsrcmgr, None)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    # Proccess pages
    pageno = 1
    for page in doc.get_pages():
        pageno = pageno + 1
        if pageno != 9:
            continue
        try:
            print "-" * 20, pageno, "-" * 20
            interpreter.process_page(page)
        except Exception, e:
            print e
            print "Error on page: %s" % pageno
            print "Marking done"
            return

    buff = device.strbuff
    #res = re.findall(r'\[\d\].*\.(?!\[)', buff)
    res = re.findall(r'\[\d\][^\[]*', buff)
    print "\n----------------------\n".join(res)

         

# main
def main(argv):
    import getopt
    def usage():
        print ('usage: %s [-d] file ...' % argv[0])
        return 100
    try:
        (opts, args) = getopt.getopt(argv[1:], 'd')
    except getopt.GetoptError:
        return usage()
    if not args: return usage()

    debug = 0

    for (k, v) in opts:
        if k == '-d': debug += 1
    
    for fname in args:
        infile = open(fname, 'rb')
        process(infile)

if __name__ == '__main__': sys.exit(main(sys.argv))
