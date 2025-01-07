import os


def static_ex_generalterm_csv():
    data = """term_id,key_name,ja,en
33c6e9dc-5787-0f96-7683-f39281c60419,sample.general.composiiton,化学式、組成式、分子式など,"Chemical formula, composition formula, molecular formula, etc."
f2d5e89e-01f0-66a2-5d8e-623a4fc31698,sample.general.material-name,物質名,Material name
a7a6fc7b-ed46-88b0-bba8-a1e34857a049,sample.general.sample-alias,試料別名,Another sample name
e2d20d02-2e38-2cd3-b1b3-66fdb8a11057,sample.general.cas-number,CAS番号,CAS Number
1e70d11d-cbdd-bfd1-9301-9612c29b4060,sample.general.purchase-date,試料購入日,Purchase date
1d3cab05-3eaa-cb9b-9a3f-20eb0ca26963,sample.general.crystalline-state,結晶状態,Crystalline state
efcf34e7-4308-c195-6691-6f4d28ffc9bb,sample.general.crystal-structure,結晶構造,Crystal structure
e9617207-7f74-ef45-9b05-74eef6e4ecbb,sample.general.pearson-symbol,ピアソン記号,Pearson symbol
f63149a4-e57c-4273-4c1e-dffa41356d28,sample.general.space-group,空間群,Space group
7cc57dfb-8b70-4b3a-5315-fbce4cbf73d0,sample.general.sample-shape,試料形状,Sample shape
efc6a0d5-313e-1871-190c-baaff7d1bf6c,sample.general.smiles-string,SMILES String,SMILES String
9270879d-d94e-4d3f-2d5c-19568e040004,sample.general.inchi,InChI,InChI
3edadcff-8a85-51d9-708f-8f76bf055377,sample.general.inchi-key,InChI key,InChI key
dc27a956-263e-f920-e574-5beec912a247,sample.general.molecular-weight,分子量,molecular weight
0444cf53-db47-b208-7b5f-54429291a140,sample.general.sample-type,試料分類,Sample type
fc30c31d-12a3-591a-c837-4f06ab458de0,sample.general.taxonomy,生物種,Taxonomy
9a23002a-c398-e521-081a-24b6cd32dbbd,sample.general.cell-line,細胞株,Cell line
b4ce4016-e2bf-e5a1-7cae-ed496c7a776f,sample.general.protein-name,タンパク名,Protein name
8c9b1a88-1530-24d3-4b2e-5441eee5c24f,sample.general.gene-name,遺伝子名,Gene name
047e30f3-f294-e58d-cbe4-6bb588bf4cf8,sample.general.ncbi-accession-number,NCBIアクセッション番号,NCBI accession number
3adf9874-7bcb-e5f8-99cb-3d6fd9d7b55e,sample.general.general-name,一般名称,General name
0aadfff2-37de-411f-883a-38b62b2abbce,sample.general.chemical-composition,化学組成,Chemical composition
5e166ac4-bfcd-457a-84bc-8626abe9188f,sample.general.supplier,購入元,Supplier
0d0417a3-3c3b-496a-b0fb-5a26f8a74166,sample.general.lot-number-or-product-number-etc,ロット番号、製造番号など,Lot number or product number etc
"""
    test_dirpath = os.path.dirname(os.path.dirname(__file__))
    test_path = os.path.join(test_dirpath, "test_general_term.csv")
    with open(test_path, mode="w", encoding="utf-8") as f:
        f.write(data)

    return test_path


def static_ex_specificterm_csv():
    data = """sample_class_id,term_id,key_name,ja,en
01cb3c01-37a4-5a43-d8ca-f523ca99a75b,3250c45d-0ed6-1438-43b5-eb679918604a,sample.specific.organic.chemical-formula,有機材料/化学式,organic material/Chemical formula
01cb3c01-37a4-5a43-d8ca-f523ca99a75b,70c2c751-5404-19b7-4a5e-981e6cebbb15,sample.specific.organic.name,有機材料/名称,organic material/Name
01cb3c01-37a4-5a43-d8ca-f523ca99a75b,e2d20d02-2e38-2cd3-b1b3-66fdb8a11057,sample.specific.organic.cas-number,有機材料/CAS番号,organic material/CAS Number
01cb3c01-37a4-5a43-d8ca-f523ca99a75b,518e26a0-4262-86f5-3598-80e18e6ff2af,sample.specific.organic.pubchem,有機材料/PubChem,organic material/PubChem
01cb3c01-37a4-5a43-d8ca-f523ca99a75b,3a775d54-5c13-fe66-6405-29c05bc931ce,sample.specific.organic.viscosity,有機材料/粘度,organic material/viscosity
01cb3c01-37a4-5a43-d8ca-f523ca99a75b,659da80e-c2ee-2986-41ce-68201b3bc4dd,sample.specific.organic.boiling-point,有機材料/沸点,organic material/boiling point
01cb3c01-37a4-5a43-d8ca-f523ca99a75b,4efc4c3b-727c-c752-cf28-701b55dba1af,sample.specific.organic.melting-temperature,有機材料/融点,organic material/Melting temperature
932e4fe1-9724-305f-ffc5-1908c31c83e5,70c2c751-5404-19b7-4a5e-981e6cebbb15,sample.specific.inorganic.name,無機材料/名称,inorganic material/Name
932e4fe1-9724-305f-ffc5-1908c31c83e5,3250c45d-0ed6-1438-43b5-eb679918604a,sample.specific.inorganic.chemical-formula,無機材料/化学式,inorganic material/Chemical formula
932e4fe1-9724-305f-ffc5-1908c31c83e5,f63149a4-e57c-4273-4c1e-dffa41356d28,sample.specific.inorganic.space-group,無機材料/空間群,inorganic material/Space group
a674a8ef-efa8-9497-4ed4-74de55fafddb,3250c45d-0ed6-1438-43b5-eb679918604a,sample.specific.metals.chemical-formula,金属・合金/化学式,metals and alloys/Chemical formula
a674a8ef-efa8-9497-4ed4-74de55fafddb,70c2c751-5404-19b7-4a5e-981e6cebbb15,sample.specific.metals.name,金属・合金/名称,metals and alloys/Name
a674a8ef-efa8-9497-4ed4-74de55fafddb,e2d20d02-2e38-2cd3-b1b3-66fdb8a11057,sample.specific.metals.cas-number,金属・合金/CAS番号,metals and alloys/CAS Number
a674a8ef-efa8-9497-4ed4-74de55fafddb,f63149a4-e57c-4273-4c1e-dffa41356d28,sample.specific.metals.space-group,金属・合金/空間群,metals and alloys/Space group
a674a8ef-efa8-9497-4ed4-74de55fafddb,efcf34e7-4308-c195-6691-6f4d28ffc9bb,sample.specific.metals.crystal-structure,金属・合金/結晶構造,metals and alloys/Crystal structure
a674a8ef-efa8-9497-4ed4-74de55fafddb,659da80e-c2ee-2986-41ce-68201b3bc4dd,sample.specific.metals.boiling-point,金属・合金/沸点,metals and alloys/boiling point
a674a8ef-efa8-9497-4ed4-74de55fafddb,4efc4c3b-727c-c752-cf28-701b55dba1af,sample.specific.metals.melting-temperature,金属・合金/融点,metals and alloys/Melting temperature
342ba516-4d02-171c-9bc4-70a3134b47a8,3250c45d-0ed6-1438-43b5-eb679918604a,sample.specific.polymers.chemical-formula,ポリマー/化学式,polymers/Chemical formula
342ba516-4d02-171c-9bc4-70a3134b47a8,70c2c751-5404-19b7-4a5e-981e6cebbb15,sample.specific.polymers.name,ポリマー/名称,polymers/Name
342ba516-4d02-171c-9bc4-70a3134b47a8,e2d20d02-2e38-2cd3-b1b3-66fdb8a11057,sample.specific.polymers.cas-number,ポリマー/CAS番号,polymers/CAS Number
342ba516-4d02-171c-9bc4-70a3134b47a8,518e26a0-4262-86f5-3598-80e18e6ff2af,sample.specific.polymers.pubchem,ポリマー/PubChem,polymers/PubChem
342ba516-4d02-171c-9bc4-70a3134b47a8,4efc4c3b-727c-c752-cf28-701b55dba1af,sample.specific.polymers.melting-temperature,ポリマー/融点,polymers/Melting temperature
52148afb-6759-23e8-c8b8-33912ec5bfcf,70c2c751-5404-19b7-4a5e-981e6cebbb15,sample.specific.semiconductors.name,半導体/名称,semiconductors/Name
961c9637-9b83-0e9d-e60e-ffc1e2517afd,70c2c751-5404-19b7-4a5e-981e6cebbb15,sample.specific.ceramics.name,セラミックス/名称,ceramics/Name
0dde5969-3039-739b-b33b-97df40450790,70c2c751-5404-19b7-4a5e-981e6cebbb15,sample.specific.biological.name,生物学的物質/名称,biological/Name
01cb3c01-37a4-5a43-d8ca-f523ca99a75b,dc27a956-263e-f920-e574-5beec912a247,sample.specific.organic-material.molecular-weight,有機材料/分子量,organic material/molecular weight
01cb3c01-37a4-5a43-d8ca-f523ca99a75b,efc6a0d5-313e-1871-190c-baaff7d1bf6c,sample.specific.organic-material.SMILES-String,有機材料/SMILES String,organic material/SMILES String
0dde5969-3039-739b-b33b-97df40450790,0444cf53-db47-b208-7b5f-54429291a140,sample.specific.biological.sample-type,生物学的物質/試料分類,biological/Sample type
0dde5969-3039-739b-b33b-97df40450790,fc30c31d-12a3-591a-c837-4f06ab458de0,sample.specific.biological.taxonomy,生物学的物質/生物種,biological/Taxonomy
0dde5969-3039-739b-b33b-97df40450790,9a23002a-c398-e521-081a-24b6cd32dbbd,sample.specific.biological.cell-line,生物学的物質/細胞株,biological/Cell line
0dde5969-3039-739b-b33b-97df40450790,b4ce4016-e2bf-e5a1-7cae-ed496c7a776f,sample.specific.biological.protein-name,生物学的物質/タンパク名,biological/Protein name
0dde5969-3039-739b-b33b-97df40450790,8c9b1a88-1530-24d3-4b2e-5441eee5c24f,sample.specific.biological.gene-name,生物学的物質/遺伝子名,biological/Gene name
0dde5969-3039-739b-b33b-97df40450790,047e30f3-f294-e58d-cbe4-6bb588bf4cf8,sample.specific.biological.ncbi-accession-number,生物学的物質/NCBIアクセッション番号,biological/NCBI accession number
01cb3c01-37a4-5a43-d8ca-f523ca99a75b,9270879d-d94e-4d3f-2d5c-19568e040004,sample.specific.organic-material.inchi,有機材料/InChI,organic material/InChI
01cb3c01-37a4-5a43-d8ca-f523ca99a75b,3edadcff-8a85-51d9-708f-8f76bf055377,sample.specific.organic-material.inchi-key,有機材料/InChI key,organic material/InChI key
"""
    test_dirpath = os.path.dirname(os.path.dirname(__file__))
    test_path = os.path.join(test_dirpath, "test_specificterm.csv")
    with open(test_path, mode="w", encoding="utf-8") as f:
        f.write(data)

    return test_path
