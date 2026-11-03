// Build a preview of the template with sample data injected, the way n8n does it.
// Usage: node tools/preview.mjs [template.html] [data.json] [out.html]
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { dirname } from 'node:path';
const [tpl = 'dirayah-template.html', data = 'preview/sample-lesson.json', out = 'shots/preview.html'] = process.argv.slice(2);
const { lesson, ayat } = JSON.parse(readFileSync(data, 'utf8'));
const html = readFileSync(tpl, 'utf8')
  .replace('/*__LESSON_JSON__*/null', JSON.stringify(lesson))
  .replace('/*__AYAT_JSON__*/null', JSON.stringify(ayat));
mkdirSync(dirname(out), { recursive: true });
writeFileSync(out, html);
console.log('wrote', out);
