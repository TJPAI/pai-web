from pathlib import Path
import re

p=Path('assets/js/site.js')
s=p.read_text(encoding='utf-8')
old="""      const step=360/data.length;
      const markup=[];
      data.forEach(([label,href],i)=>{
        const center=i*step;
        const chars=Array.from(label);
        const ascii=chars.every(ch=>/[\\x00-\\x7F]/.test(ch));
        const charStep=ascii
          ? (chars.length<=4?5.0:Math.min(3.6,32/Math.max(1,chars.length-1)))
          : (chars.length<=2?7.8:7.6);
        markup.push(`<a class=\"pai-orbit-item\" aria-label=\"${label}\" href=\"${root(href)}\" style=\"--item-angle:${center}deg\"><span class=\"pai-orbit-sr\">${label}</span></a>`);
        chars.forEach((ch,j)=>{
          const offset=(j-(chars.length-1)/2)*charStep;
          markup.push(`<span class=\"pai-orbit-char\" aria-hidden=\"true\" style=\"--char-angle:${center+offset}deg\">${ch}</span>`);
        });
      });"""
new="""      const markup=[];
      const layout=data.map(([label,href])=>{
        const chars=Array.from(label);
        const ascii=chars.every(ch=>/[\\x00-\\x7F]/.test(ch));
        const charStep=ascii
          ? (chars.length<=4?5.0:Math.min(3.6,32/Math.max(1,chars.length-1)))
          : (chars.length<=2?7.8:7.6);
        /* Approximate the visible angular width of the end glyphs as well as
           the centre-to-centre character spacing. This lets us equalise the
           actual blank arc between neighbouring labels, not their centres. */
        const glyphSpan=ascii?4.6:6.4;
        const span=(Math.max(0,chars.length-1)*charStep)+glyphSpan;
        return {label,href,chars,charStep,span,center:0};
      });
      const used=layout.reduce((sum,item)=>sum+item.span,0);
      const gap=Math.max(0,(360-used)/layout.length);
      /* Keep Home at 12 o'clock, then place every following label from the
         previous visible edge + one identical gap. The final wrap-around gap
         is identical by construction because spans + gaps total 360 degrees. */
      for(let i=1;i<layout.length;i++){
        const prev=layout[i-1];
        const item=layout[i];
        item.center=prev.center+prev.span/2+gap+item.span/2;
      }
      layout.forEach(({label,href,chars,charStep,center})=>{
        markup.push(`<a class=\"pai-orbit-item\" aria-label=\"${label}\" href=\"${root(href)}\" style=\"--item-angle:${center}deg\"><span class=\"pai-orbit-sr\">${label}</span></a>`);
        chars.forEach((ch,j)=>{
          const offset=(j-(chars.length-1)/2)*charStep;
          markup.push(`<span class=\"pai-orbit-char\" aria-hidden=\"true\" style=\"--char-angle:${center+offset}deg\">${ch}</span>`);
        });
      });"""
if old not in s:
    raise SystemExit('orbit layout block not found')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')

# Bump only the JS cache token; CSS is unchanged.
for html in Path('.').rglob('*.html'):
    text=html.read_text(encoding='utf-8')
    text=re.sub(r'site\\.js\\?v=[^\"\\\']+','site.js?v=20260920-64',text)
    html.write_text(text,encoding='utf-8')
