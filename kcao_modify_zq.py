from nltk.tokenize.treebank import TreebankWordTokenizer
from nltk import PunktSentenceTokenizer, RegexpTokenizer
import glob
import json
import re
import random
import nltk

pattern = re.compile(r'''(?x)   # set flag to allow verbose regexps: ignores spaces and newlines
        (?:[A-Z]\.)+            # abbreviations, e.g. U.S.A.
        | \$?\d+(?:\.\d+)?%?    # currency and percentages, e.g. $12.40, 82%
        | '(?:s|nt)\b           # 's, 'nt
        #     | \w+(?:-\w+)*    # words with optional internal hyphens
        | [a-zA-Z0-9]+          # words without internal hyphens e.g. manual-enforced Type1_gene(Attention: \w contains _)
        | \.\.\.                # ellipsis
        | [.,;"?:]              # these are separate tokens
        | [][()_`\|\n-]+        # these tokens are grouped; includes ] and [ and -
        ''')
random.seed(1)
MARKER="OBI"
def select_train_test(file,ratio=0.7):   #file is list 
    random.shuffle(file)
    train_len=int(len(file)*ratio)
    return file[:train_len], file[train_len:]

def write_row(outfile,token,pos,marker,entity=None):
    if entity is None:
        outfile.write("".join((token,"\t",pos,"\t",marker,"\n")))
    else:
        outfile.write("".join((token,"\t",pos,"\t",marker,"-",entity,"\n")))

def write_text(input,output):                                 ###inpur :list of file  output:a file
    outfile=open(output,"w",encoding='utf-8',newline="\n")
    num=0
    for file in input:
        with open(file) as f:
            source=json.loads(f.read())
            text=source["text"]
            target_info=source["target"]
            outfile.write("".join(["#"*20,"source_",repr(num),"_from",":",target_info])+"\n")
            outfile.write(text+"\n")
            outfile.write("\n".join([repr(i) for i in source["denotations"]])+"\n"*2)
            num+=1
    outfile.write("\n"*2+"*"*20+"Finish! the numver of pubmed source is : "+str(num))
            
            


def json_to_tab(input,output):
    outfile=open(output,"w",encoding="utf-8",newline="\n")
    for file in input:
        with open(file) as f:
            source=json.loads(f.read())
            text=source["text"].replace("\n"," ")
            sent_span = list(sent_tokenizer.span_tokenize(text))
            token_span = list(word_tokenizer.span_tokenize(text))
            pos_tag=[pos[1] for st, ed in sent_span 
                            for pos in nltk.pos_tag(word_tokenizer.tokenize(text[st: ed]))]
            denotations=source["denotations"]
            denotation_span=[(i["span"]["begin"],i["span"]["end"]) for i in denotations]
            sent_index=0                                    ###句子索引
            sent_end=sent_span[sent_index][-1]
            
            cur=0                                           ###注释索引
            ###给一个虚拟的denotation
            denotations.append({'obj': None, 'span': {'begin': len(text), 'end': len(text)}})
            
            
            
            ###sentence judgment  可能耗时！！！
            record=[]
            for i in range(len(sent_span)):
                for den_start, den_end in denotation_span:
                    if den_start >= sent_span[i][0] and den_end <= sent_span[i][1]:
                        record.append(i)
                        break
            if len(record) > 0:
                print(set(range(len(sent_span))) - set(record), "these sentence have not annotations!")

            ####识别换行
            for index, (token_start, token_end) in enumerate(token_span):
                if index in record:
                    continue
                if token_end==token_span[-1][1]:
                    break
                if token_start >= sent_end:
                    if sent_index not in record:
                        outfile.write("\n")
                    sent_index += 1
                    if sent_index<=len(sent_span)-1:
                        sent_end=sent_span[sent_index][-1]     ####作用是在一句话后加入一个空行



                if  cur and cur <= len(denotations)-1:
                    last_end=denotations[cur-1]["span"]["end"]    ###上一个标注的结尾坐标
                    while denotations[cur]["span"]["begin"]<last_end:
                        print("pass one repeat denotations")
                        cur += 1
                    if cur==len(denotations):
                        break
                        
                    ######   cur_denote都可以直接用cur来判断 
                cur_denote = denotations[cur]
                
                
                
                
                
                ###最重要的部分：标注    
                start=cur_denote["span"]["begin"]
                end=cur_denote["span"]["end"]
                entity=cur_denote["obj"]
                token = text[token_start: token_end]
                pos=pos_tag[index]
                
                if token_end<=start:
                    ###判断token是否在没有标注的sent_span上
                    count=0
                    for i in range(len(record)):
                        if token_start >= sent_span[i][0] and token_end <= sent_span[i][1]:
                            count+=1
                            break
                    if count==0:
                        write_row(outfile,token,pos,MARKER[0])
                        
                        
                elif token_start ==start:                         ###判断注释里面有多少个token
                    write_row(outfile,token,pos,MARKER[1],entity)
                    if token_end==end:
                        cur += 1
                elif token_start>start:
                    if token_span[index-1][0] >=start:
                        # e.g. token: of   marker: gain of function
                        write_row(outfile,token,pos,MARKER[2],entity)  ###判断为I
                    if token_end >= end:
                        cur += 1
                        
                else:
                    print(">>>error")
                    print(file,token_start,token_end,cur)
        outfile.write("\n")
        print("converting: ",file, " done")
    outfile.close()



files = list(glob.iglob('*json'))
train, test = select_train_test(files, 0.8)
word_tokenizer = RegexpTokenizer(pattern)
sent_tokenizer = PunktSentenceTokenizer()

json_to_tab(files, "all.tab")
json_to_tab(train, "train.tab")
json_to_tab(test, "test.tab")
# files=["PubMed-28934391.json","PubMed-29372308.json"]
write_text(files, 'all_text_denos')
