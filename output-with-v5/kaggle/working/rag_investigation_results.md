# RAG Investigation: Why These Cases Got WORSE

**Generated:** 2026-01-11 12:05:11

======================================================================

**Analysis:** Cases where Baseline was correct but RAG predicted wrong
**Total Cases to Investigate:** 7

======================================================================


## Case 1: es-EC_026

----------------------------------------------------------------------

**Question:** What is Ecuador's official currency since the year 2000?

**Correct Answer:** C - United States Dollar

**Baseline Predicted:** C ✅ - United States Dollar

**RAG Predicted:** D ❌ - New Sol

### Retrieval Context
- **Country Filter:** EC
- **Intent:** economy_currency_symbols

### Retrieved Chunks (3 total)

#### Chunk 1
- **Source:** `bbc.co.uk`
- **Trust Level:** `unknown`
- **Score:** `0.0194`
- ❌ **Does NOT contain correct answer:** 'United States Dollar'

**Text Preview:**
```
Dementia Jersey Ecuador volcano trek raises £25,000Islanders took on the Avenue of Volcanoes challenge in Ecuador and raised £25k for Dementia Jersey.Published29 December 2025SiteNews
...
```

#### Chunk 2
- **Source:** `bbc.co.uk`
- **Trust Level:** `unknown`
- **Score:** `0.0191`
- ❌ **Does NOT contain correct answer:** 'United States Dollar'

**Text Preview:**
```
Dementia Jersey Ecuador volcano trek raises £25,000
...
```

#### Chunk 3
- **Source:** `bbc.co.uk`
- **Trust Level:** `unknown`
- **Score:** `0.0186`
- ❌ **Does NOT contain correct answer:** 'United States Dollar'

**Text Preview:**
```
Islanders took on the Avenue of Volcanoes challenge in Ecuador and raised £25k for Dementia Jersey.
...
```

----------------------------------------------------------------------

## Case 2: es-MX_049

----------------------------------------------------------------------

**Question:** What is the most typical street food in the country?

**Correct Answer:** C - Tacos

**Baseline Predicted:** C ✅ - Tacos

**RAG Predicted:** D ❌ - Paella

### Retrieval Context
- **Country Filter:** MX
- **Intent:** food_drink

### Retrieved Chunks (4 total)

#### Chunk 1
- **Source:** `bbc.co.uk`
- **Trust Level:** `unknown`
- **Score:** `0.0192`
- ❌ **Does NOT contain correct answer:** 'Tacos'

**Text Preview:**
```
NFL: Seattle Seahawks beat San Francisco 49ers to claim top spot in NFC
...
```

#### Chunk 2
- **Source:** `bbc.co.uk`
- **Trust Level:** `unknown`
- **Score:** `0.0098`
- ❌ **Does NOT contain correct answer:** 'Tacos'

**Text Preview:**
```
NFL: Seattle Seahawks beat San Francisco 49ers to claim top spot in NFCThe Seattle Seahawks beat the San Francisco 49ers 13-3 to secure the NFC West title and top spot in the NFC.Published7 days agoSiteSport
...
```

#### Chunk 3
- **Source:** `bbc.co.uk`
- **Trust Level:** `unknown`
- **Score:** `0.0098`
- ❌ **Does NOT contain correct answer:** 'Tacos'

**Text Preview:**
```
West Ham news: Fan views on Nuno Espirito Santo futurePublished3 days agoSiteSport
...
```

#### Chunk 4
- **Source:** `bbc.co.uk`
- **Trust Level:** `unknown`
- **Score:** `0.0097`
- ❌ **Does NOT contain correct answer:** 'Tacos'

**Text Preview:**
```
The Seattle Seahawks beat the San Francisco 49ers 13-3 to secure the NFC West title and top spot in the NFC.
...
```

----------------------------------------------------------------------

## Case 3: ko-KR_056

----------------------------------------------------------------------

**Question:** Which is NOT a traditional Korean play?

**Correct Answer:** B - Sumo

**Baseline Predicted:** B ✅ - Sumo

**RAG Predicted:** C ❌ - Flipping game cards

### Retrieval Context
- **Country Filter:** KR
- **Intent:** holidays_festivals

### Retrieved Chunks (3 total)

#### Chunk 1
- **Source:** `crokepark.ie`
- **Trust Level:** `unknown`
- **Score:** `0.0146`
- ❌ **Does NOT contain correct answer:** 'Sumo'

**Text Preview:**
```
Here you will find everything you need to know about the next upcoming game in Croke Park and future fixtures – how to get here, where to go when you arrive and the facilities on-hand to make your day out as safe and as enjoyable as possible!
...
```

#### Chunk 2
- **Source:** `crokepark.ie`
- **Trust Level:** `unknown`
- **Score:** `0.0145`
- ❌ **Does NOT contain correct answer:** 'Sumo'

**Text Preview:**
```
Here you will find everything you need to know about the next upcoming game in Croke Park and future fixtures – how to get here, where to go when you arrive and the facilities on-hand to make your day out as safe and as enjoyable as possible!
...
```

#### Chunk 3
- **Source:** `crokepark.ie`
- **Trust Level:** `unknown`
- **Score:** `0.0143`
- ❌ **Does NOT contain correct answer:** 'Sumo'

**Text Preview:**
```
Here you will find everything you need to know about the next upcoming game in Croke Park and future fixtures – how to get here, where to go when you arrive and the facilities on-hand to make your day out as safe and as enjoyable as possible!
...
```

----------------------------------------------------------------------

## Case 4: fr-FR_112

----------------------------------------------------------------------

**Question:** What fruit changes its name when dried?

**Correct Answer:** C - Grape

**Baseline Predicted:** C ✅ - Grape

**RAG Predicted:** D ❌ - Tomato

### Retrieval Context
- **Country Filter:** FR
- **Intent:** other

### Retrieved Chunks (2 total)

#### Chunk 1
- **Source:** `france.fr`
- **Trust Level:** `unknown`
- **Score:** `0.0098`
- ❌ **Does NOT contain correct answer:** 'Grape'

**Text Preview:**
```
5 minutes pour tout savoir sur la clémentine de CorseCorsica
...
```

#### Chunk 2
- **Source:** `pop.culture.gouv.fr`
- **Trust Level:** `unknown`
- **Score:** `0.0097`
- ❌ **Does NOT contain correct answer:** 'Grape'

**Text Preview:**
```
POP décrit et diffuse des notices de biens culturels conservés en France, à découvrir par base de données.
...
```

----------------------------------------------------------------------

## Case 5: ta-LK_121

----------------------------------------------------------------------

**Question:** What is the tallest building in Sri Lanka?

**Correct Answer:** A - Lotus Tower

**Baseline Predicted:** A ✅ - Lotus Tower

**RAG Predicted:** B ❌ - One Galle Face

### Retrieval Context
- **Country Filter:** LK
- **Intent:** economy_currency_symbols

### Retrieved Chunks (3 total)

#### Chunk 1
- **Source:** `srilanka.travel`
- **Trust Level:** `unknown`
- **Score:** `0.0184`
- ❌ **Does NOT contain correct answer:** 'Lotus Tower'

**Text Preview:**
```
The first thing you should do is contact the seller directly.
...
```

#### Chunk 2
- **Source:** `srilanka.travel`
- **Trust Level:** `unknown`
- **Score:** `0.0181`
- ❌ **Does NOT contain correct answer:** 'Lotus Tower'

**Text Preview:**
```
The first thing you should do is contact the seller directly.
...
```

#### Chunk 3
- **Source:** `srilanka.travel`
- **Trust Level:** `unknown`
- **Score:** `0.0179`
- ❌ **Does NOT contain correct answer:** 'Lotus Tower'

**Text Preview:**
```
The first thing you should do is contact the seller directly.
...
```

----------------------------------------------------------------------

## Case 6: tl-PH_130

----------------------------------------------------------------------

**Question:** Who is considered the national hero of the Philippines?

**Correct Answer:** D - Jose Rizal

**Baseline Predicted:** D ✅ - Jose Rizal

**RAG Predicted:** A ❌ - Andres Bonifacio

### Retrieval Context
- **Country Filter:** PH
- **Intent:** other

### Retrieved Chunks (3 total)

#### Chunk 1
- **Source:** `philippines.travel`
- **Trust Level:** `unknown`
- **Score:** `0.0098`
- ❌ **Does NOT contain correct answer:** 'Jose Rizal'

**Text Preview:**
```
World's best island featuring El Nido lagoons, Coron wrecks, and UNESCO Underground River.
...
```

#### Chunk 2
- **Source:** `philippines.travel`
- **Trust Level:** `unknown`
- **Score:** `0.0097`
- ❌ **Does NOT contain correct answer:** 'Jose Rizal'

**Text Preview:**
```
World's best island featuring El Nido lagoons, Coron wrecks, and UNESCO Underground River.
...
```

#### Chunk 3
- **Source:** `philippines.travel`
- **Trust Level:** `unknown`
- **Score:** `0.0095`
- ❌ **Does NOT contain correct answer:** 'Jose Rizal'

**Text Preview:**
```
World's best island featuring El Nido lagoons, Coron wrecks, and UNESCO Underground River.
...
```

----------------------------------------------------------------------

## Case 7: ja-JP_143

----------------------------------------------------------------------

**Question:** What is a typical Japanese breakfast?

**Correct Answer:** B - Miso soup

**Baseline Predicted:** B ✅ - Miso soup

**RAG Predicted:** C ❌ - Baguette

### Retrieval Context
- **Country Filter:** JP
- **Intent:** food_drink

### Retrieved Chunks (5 total)

#### Chunk 1
- **Source:** `bunka.nii.ac.jp`
- **Trust Level:** `unknown`
- **Score:** `0.0098`
- ❌ **Does NOT contain correct answer:** 'Miso soup'

**Text Preview:**
```
12/18（木）16時頃から断続的に一部サービスが停止しておりました。ご利用の皆さまにはご不便とご迷惑をおかけいたしましたこと、深くお詫び申し上げます。
...
```

#### Chunk 2
- **Source:** `bunka.nii.ac.jp`
- **Trust Level:** `unknown`
- **Score:** `0.0097`
- ❌ **Does NOT contain correct answer:** 'Miso soup'

**Text Preview:**
```
12/18（木）16時頃から断続的に一部サービスが停止しておりました。ご利用の皆さまにはご不便とご迷惑をおかけいたしましたこと、深くお詫び申し上げます。
...
```

#### Chunk 3
- **Source:** `bunka.nii.ac.jp`
- **Trust Level:** `unknown`
- **Score:** `0.0095`
- ❌ **Does NOT contain correct answer:** 'Miso soup'

**Text Preview:**
```
12/18（木）16時頃から断続的に一部サービスが停止しておりました。ご利用の皆さまにはご不便とご迷惑をおかけいたしましたこと、深くお詫び申し上げます。
...
```

#### Chunk 4
- **Source:** `bunka.nii.ac.jp`
- **Trust Level:** `unknown`
- **Score:** `0.0094`
- ❌ **Does NOT contain correct answer:** 'Miso soup'

**Text Preview:**
```
12/18（木）16時頃から断続的に一部サービスが停止しておりました。ご利用の皆さまにはご不便とご迷惑をおかけいたしましたこと、深くお詫び申し上げます。
...
```

#### Chunk 5
- **Source:** `bunka.nii.ac.jp`
- **Trust Level:** `unknown`
- **Score:** `0.0092`
- ❌ **Does NOT contain correct answer:** 'Miso soup'

**Text Preview:**
```
文化遺産オンラインは、文化庁が運営する我が国の文化遺産についてのポータルサイトです。 全国の博物館・美術館等から提供された作品や国宝・重要文化財など、さまざまな情報をご覧いただけます。
...
```

----------------------------------------------------------------------

======================================================================

## ✅ INVESTIGATION COMPLETE - ALL 7 CASES ANALYZED

======================================================================
