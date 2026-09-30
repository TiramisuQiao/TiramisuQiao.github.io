import markdownIt from 'markdown-it';
import markdownItAnchor from 'markdown-it-anchor';

export default function (eleventyConfig) {
  eleventyConfig.setLibrary('md', markdownIt({ html: true, typographer: true }).use(markdownItAnchor));
  eleventyConfig.addPassthroughCopy({ 'src/assets': 'assets' });
  eleventyConfig.addFilter('year', () => new Date().getFullYear());
  return {
    dir: { input: 'src', includes: '_includes', output: '_site' },
    markdownTemplateEngine: 'njk',
    htmlTemplateEngine: 'njk',
  };
}
