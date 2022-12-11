# Read John Guittar trait's table
tr_guitar = pd.read_csv('curated_trait_data.csv', index_col=0)
tr_guitar.head()


# Read tresor's table and carrying out data checking and cleaning
import pandas as pd
from tqdm import tqdm
tr_tresor = pd.read_excel('traitdata_tresor.xlsx')
tr_tresor = tr_tresor[pd.notnull(tr_tresor['Genus']) & pd.notnull(tr_tresor['Species'])]

# strip names
for col in ['Genus', 'Species']:
    tr_tresor[col] = tr_tresor[col].apply(lambda x: x.strip())

# fix multiwords
for (genus, species), g in tqdm(tr_tresor.groupby(['Genus', 'Species'])):
    if species.startswith(genus):
        tr_tresor.loc[g.index, 'Species'] = species[len(genus):]

# drop subsp.
for idx, row in tqdm(find_multiword_rows(tr_tresor, ['Genus', 'Species']).iterrows()):
    if ' subsp. ' in row['Species']:
        parts = row['Species'].split(' subsp. ')
        if len(parts) > 1:
            tr_tresor.loc[idx, 'Species'] = parts[0]
    if '\xa0subsp. ' in row['Species']:
        parts = row['Species'].split('\xa0subsp. ')
        if len(parts) > 1:
            tr_tresor.loc[idx, 'Species'] = parts[0]

# manual fixes
idx = tr_tresor[tr_tresor['Genus'] == "Mucilaginibacter rigui"].index
tr_tresor.loc[idx, 'Species'] = 'rigui'
tr_tresor.loc[idx, 'Genus'] = 'Mucilaginibacter'

idx = tr_tresor[(tr_tresor['Genus'] == "Sphingobacterium") & (tr_tresor['Species'] == ' composti [homonym]')].index
tr_tresor.loc[idx, 'Species'] = 'composti'

idx = tr_tresor[(tr_tresor['Genus'] == "Plasticicumulans") & (tr_tresor['Species'] == 'not yet known; article proposed:Plasticicumulans lactativoran')].index
tr_tresor.loc[idx, 'Species'] = 'lactativorans'

idx = tr_tresor[(tr_tresor['Genus'] == "Mycobacterium gordonae")].index
tr_tresor.loc[idx, 'Genus'] = 'Mycobacterium'
tr_tresor.loc[idx, 'Species'] = 'gordonae'

tr_tresor.head()

# Comparing trait information in both data tables
res = []
for trait in sorted(tr_guitar.columns[2:]):
    res.append({'source': 'guittar', 'trait': trait, 
                'No of trait information': tr_guitar[trait].dropna().shape[0], 
                'nonempty_collapsed': len(tr_guitar.dropna(subset=[trait]).groupby(['Genus','Species']))})
    res.append({'source': 'tresor', 'trait': trait, 
                'No of trait information': tr_tresor[tr_tresor['trait'] == trait]['val'].dropna().shape[0], 
                'nonempty_collapsed': len(tr_tresor[tr_tresor['trait'] == trait].dropna().groupby(['Genus', 'Species']))})
res = pd.DataFrame(res)
res.head()


# Data visualization
# Venn Diagram

import pylab as plt
from matplotlib_venn import venn2, venn2_circles, venn3, venn3_circles
fig, axes = plt.subplots(1,2, figsize=(10,4))
for level, ax in zip(['Genus', 'Species'], axes):
    g = set(tr_guitar[level].unique())
    t = set(tr_tresor[level].unique())
    venn2([g, t], ['Guittar et al.', 'Tresor'], ax=ax)
    ax.set_title(level)
    if level == 'Genus':
        print(g-t)
plt.savefig('venndiagram.svg',bbox_inches = "tight") 

# Bar charts
import seaborn as sns
fig, axes = plt.subplots(1,1,figsize=(4,12))
sns.barplot(data=res, y='trait', x='No of trait information', hue='source', ax=axes)
plt.savefig('barplot.svg',bbox_inches = "tight")

fig, axes = plt.subplots(1,1,figsize=(4,12))
sns.barplot(data=res, y='trait', x='nonempty_collapsed', hue='source', ax=axes)

# What is the difference between spore score and sporulation?

x = pd.pivot_table(data=tr_tresor[tr_tresor['trait'].isin(['Sporulation'])], index=['Genus','Species'], columns='trait', values='val')
x[pd.notnull(x['Sporulation']) & pd.notnull(x['Sporulation'])]

tr_tresor[tr_tresor['trait'].isin(['Spore_score'])]

# Set threshold values
threshs = {
    'Aggregation_score': (None, None),
    'B_vitamins': (None, None),
    'Copies_16S': (None, 20),
    'GC_content': (20, 80),
    'Gene_number': (None, 11000), 
    'Genome_Mb': (None, 14),
    'Gram_positive': (None, None),
    'IgA': (None, None),
    'Length': (None, 10),
    'Motility': (None, None),
    'Oxygen_tolerance': (None, None),
    'pH_optimum': (2.5, None),
    'Salt_optimum': (None, 25),
    'Temp_optimum': (None, 80),
    'Width': (None, 5),
    'Sporulation': (None, None),}


# combine both tables
g = tr_guitar[set(tr_guitar.columns) - set(['Genus', 'Species'])].stack().reset_index().rename(columns={'level_1': 'trait', 0: 'val'})
del g['level_0']
g['source'] = 'Guittar'

t = tr_tresor[~tr_tresor['trait'].isin(['Spore','Spore_score'])][['trait','val']]
t['source'] = 'Tresor'

both = pd.concat([g,t])

data=both#[both['trait'].isin(['Motility','Oxygen_tolerance'])]

# comparing the number of trait information for both tables

for i, (trait, g) in enumerate(data.groupby('trait')):
    print(trait)
    display(g.groupby('source').size())
    
# Violin plots

numtraits = data['trait'].unique().shape[0]
fig, axes = plt.subplots(1, numtraits, figsize=(5*numtraits, 5))

for i, (trait, g) in enumerate(data.groupby('trait')):
    ax = axes[i]
    if False:
        #sns.violinplot(data=g, y='val', ax=ax, x='source')
        for source, g_source in g.groupby('source'):
            sns.distplot(g_source['val'], ax=ax, label=source)
        ax.set_title(trait)
    
    
    sns.violinplot(data=g, y="val", x="trait", hue="source",
                   split=True, inner="quart", linewidth=1,
                   palette={"Guittar": ".55", "Tresor": ".85"}, ax=ax
                  )
    for j in [0,1]:
        if threshs[trait][j] is not None:
            ax.axhline(y=threshs[trait][j], color='r', linestyle='-')
    #sns.despine(left=True)

plt.savefig('violinplot.svg',bbox_inches = "tight", orientation = 'portrait')

# Box and whisker plots
fig, axes = plt.subplots(1, numtraits, figsize=(5*numtraits, 5))

for i, (trait, g) in enumerate(data.groupby('trait')):
    ax = axes[i]
    if False:
        #sns.violinplot(data=g, y='val', ax=ax, x='source')
        for source, g_source in g.groupby('source'):
            sns.distplot(g_source['val'], ax=ax, label=source)
        ax.set_title(trait)
    
    
    sns.boxplot(data=g, y="val", x="trait", hue="source",
                   
                   palette={"Guittar": ".55", "Tresor": ".85"}, ax=ax
                  )
    for j in [0,1]:
        if threshs[trait][j] is not None:
            ax.axhline(y=threshs[trait][j], color='r', linestyle='-')
plt.savefig('boxplot.svg',bbox_inches = "tight", orientation = 'portrait')

# Correlation analysis
# checking for differences or dissimilarities in trait coding system or checking for changes of trait score for a given bacterial species

import random
traits = [c for c in tr_guitar.columns[2:]]

fig, axes = plt.subplots(1, len(traits), figsize=(5*len(traits), 5))

for i, trait in enumerate(traits):
    g = tr_guitar.set_index(['Genus','Species'])[[trait]].dropna()
    g['source'] = 'Guitar'

    t = pd.pivot_table(data=tr_tresor[tr_tresor['trait'] == trait], index=['Genus','Species'], columns='trait', values='val')
    t['source'] = 'Tresor'

    both = g.merge(t, left_index=True, right_index=True, suffixes=('_Guitar', '_Tresor')).reset_index()
    x = both['%s_Guitar' % trait]
    y = both['%s_Tresor' % trait]

    distort = 0# 0.1
    x = x.apply(lambda x: x * (1 - (random.random()*distort)))
    y = y.apply(lambda x: x * (1 - (random.random()*distort)))
    
    ax = axes[i]
    sns.scatterplot(x, y, ax=ax)
    
    #break
#both
plt.savefig('correlationplot.svg',bbox_inches = "tight", orientation = 'portrait')
