DECODER=cyrf6936

DECODERDIR=$(shell strings $$(ldconfig -p | sed -n -e '/libsigrokdecode.so /{s\#.* => \#\#;p}') | sed -n -e '/\/decoders/p')
OUTFILE=$(shell echo "samples-$$(date +%Y%m%d%H%M%S).srzip")

SIGROKCLI=sigrok-cli
SIGROKCLI_SAMPLE_OPTS=--driver fx2lafw --config samplerate=250khz --time 7s -C D0=CLK,D1=IRQ,D2=nCS,D3=MOSI,D4=MISO,D7=RST
SIGROKCLI_OUTPUT_OPTS=-P spi:wordsize=8:clk=CLK:cs=nCS:mosi=MOSI:miso=MISO,cyrf6936:delaysplit=2000 -A cyrf6936=write:read:wait

SAMPLEFILES=sample.srzip
ANNOTFILES=$(SAMPLEFILES:.srzip=-annot.txt)

$(ANNOTFILES): $(SAMPLEFILES)
	$(SIGROKCLI) -i $< $(SIGROKCLI_OUTPUT_OPTS) | sed -e 's/delay\(.*\)/\ndelay\1\n/' > $@

all: $(ANNOTFILES)
	@true

$(OUTFILE):
	$(SIGROKCLI) -o $@ $(SIGROKCLI_SAMPLE_OPTS) 

sample: $(OUTFILE)
	@true

install:
	echo sudo ln -s . $(DECODERDIR)/$(DECODER)


