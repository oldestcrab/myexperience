import re

# a = 'H00048  Hepatocellular carcinoma [PATH:hsa05225 hsa05203 hsa05161 hsa05160 hsa05206]'
# a = 'H00048  Hepatocellular carcinoma'
a = 'CTLA-4 (polymorphism) [HSA:1493] [KO:K06538]'
print(re.search(r'(.*?)\[.*\]', a).group(1))
c = re.sub(r'\(.*\)','',re.search(r'(.*?)\[.*\]', a).group(1))
print(c)

['11-BETA-HSD3,100174880,"Abnormalities, Drug-Induced",MESH:D000014,,Endocrine Disruptors,5.16,,22659286']
