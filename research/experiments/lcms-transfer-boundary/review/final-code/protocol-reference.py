"""Protocol design arithmetic only; no library import, CMM or image operation."""
from decimal import Decimal, localcontext, ROUND_FLOOR
import json
D=Decimal
with localcontext() as context:
    context.prec=80
    def decode(x):
        return x/D('12.92') if x<=D('0.04045') else ((x+D('0.055'))/D('1.055'))**D('2.4')
    def encode(x):
        return D('12.92')*x if x<=D('0.0031308') else D('1.055')*(x**(D(1)/D('2.4')))-D('0.055')
    def quant(x):return int((x*255+D('0.5')).to_integral_value(rounding=ROUND_FLOOR))
    source=[D(n)/255 for n in (128,64,192)]; linear=[decode(x) for x in source]; rows=[]
    for a in (D(128)/255,D(1)):
        encoded=[x*a for x in source];working=[x*a for x in linear];converted=[encode(x) for x in working]
        margins=[]
        for x in converted:
            scaled=x*255;lo=scaled.to_integral_value(rounding=ROUND_FLOOR)
            margins.append(abs(scaled-(lo+D('0.5'))))
        rows.append({'alpha':str(a),'encoded_direct':[str(x) for x in encoded], 'linear_composite':[str(x) for x in working], 'encoded_from_linear':[str(x) for x in converted], 'direct_quantized':[quant(x) for x in encoded], 'linear_quantized':[quant(x) for x in converted], 'channel_separation':[str(abs(x-y)) for x,y in zip(converted,encoded)],'distance_to_nearest_round_boundary_codes':[str(x) for x in margins]})
    result={'scope':'unexecuted native protocol; Decimal design reference only','decimal_precision':80,'source_encoded':[str(x) for x in source], 'source_linear':[str(x) for x in linear], 'rows':rows,'tolerance_normalized':'0.0001','tolerance_code_values':'0.0255'}
    print(json.dumps(result,indent=2))
