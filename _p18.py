p='build_mp.py'; s=open(p).read()
s=s.replace("segs = [re.sub(r'^(此造是|此造为|此人是|此人为|此造|此人|该造|本造)', '', x) for x in re.split(r'[，。；：、！？（）()]', sums) if x]",
"sums2 = re.sub(r'(闲注|分析|断|解|注)[:：]', '，', sums)\n        segs = [re.sub(r'^(此造是|此造为|此人是|此人为|此造|此人|该造|本造)', '', x) for x in re.split(r'[，。；：:、！？（）()\\.\\s]', sums2) if x]\n        segs = [x for x in segs if sum(c in GAN + ZHI for c in x) <= len(x) * 0.4]")
open(p,'w').write(s)
