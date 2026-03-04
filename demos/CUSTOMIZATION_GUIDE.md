# Customization Guide for Demo Website Templates

This guide will help you customize any of the demo website templates to fit your specific needs.

## Quick Start

1. **Download the Template**
   - Navigate to the template folder you want to use (e.g., `restaurant/`, `law-firm/`, etc.)
   - Copy the `index.html` file to your computer

2. **Preview Locally**
   ```bash
   # Navigate to the template directory
   cd restaurant/  # or any other template
   
   # Start a local server
   python3 -m http.server 8000
   
   # Open in browser
   # Go to http://localhost:8000
   ```

3. **Customize Content**
   - Open `index.html` in any text editor (VS Code, Sublime Text, Notepad++)
   - Replace placeholder text, images, and contact information
   - Look for `<!-- CUSTOMIZE -->` comments for guidance

## Common Customizations

### 1. Update Colors

Find the `tailwind.config` script in the `<head>` section and modify the color scheme:

```javascript
tailwind.config = {
    theme: {
        extend: {
            colors: {
                'brand': '#YOUR_COLOR_HEX',  // Primary brand color
                'dark': '#YOUR_DARK_HEX',    // Dark background color
                // ... other colors
            }
        }
    }
}
```

### 2. Change Fonts

Replace Google Fonts URLs in the `<head>`:

```html
<!-- Replace these URLs with your preferred fonts -->
<link href="https://fonts.googleapis.com/css2?family=Your+Font:wght@300;400;500;600;700&display=swap" rel="stylesheet">
```

Then update the font-family references in `tailwind.config`:

```javascript
fontFamily: {
    'display': ['Your Font Name', 'sans-serif'],
    'body': ['Your Body Font', 'sans-serif'],
}
```

### 3. Replace Images

Find `<img>` tags and replace the `src` attribute with your own image URLs:

```html
<!-- Before -->
<img src="https://images.unsplash.com/..." alt="Placeholder">

<!-- After - Replace with your image URL -->
<img src="images/your-photo.jpg" alt="Your Description">
```

**Image sources:**
- **Local images:** Put images in an `images/` folder next to index.html and reference as `images/filename.jpg`
- **Online images:** Use any image hosting service (Unsplash, Cloudinary, AWS S3, etc.)

### 4. Set Up Contact Forms

All templates use Formspree for contact forms (free tier):

1. Go to [formspree.io](https://formspree.io) and create a free account
2. Create a new form and copy the form endpoint (looks like: `https://formspree.io/f/abcd1234`)
3. Find the `<form>` tag in the HTML and replace `YOUR_FORMSPREE_ID` with your endpoint:

```html
<!-- Before -->
<form action="https://formspree.io/f/YOUR_FORMSPREE_ID" method="POST">

<!-- After -->
<form action="https://formspree.io/f/abcd1234" method="POST">
```

**Alternative form services:**
- Netlify Forms (free with Netlify hosting)
- Formspree (free tier: 50 submissions/month)
- Getform (free tier: 100 submissions/month)

### 5. Update Navigation Links

Find the `<nav>` section and update links:

```html
<nav>
    <a href="#home">Home</a>
    <a href="#about">About</a>
    <!-- Add or remove sections as needed -->
</nav>
```

### 6. Add Your Logo

Replace the text logo with your own image:

```html
<!-- Before -->
<a href="#" class="font-display text-2xl font-bold">Your Business</a>

<!-- After -->
<img src="images/logo.png" alt="Your Logo" class="h-10">
```

### 7. Update SEO Meta Tags

Find the meta tags in the `<head>` section:

```html
<meta name="description" content="Your business description here">
<meta name="keywords" content="your, keywords, here">
<title>Your Business Name | Your Tagline</title>
```

### 8. Add Social Media Links

Find the footer section and update social links:

```html
<a href="https://twitter.com/yourhandle">Twitter</a>
<a href="https://linkedin.com/company/yourcompany">LinkedIn</a>
<a href="https://instagram.com/yourhandle">Instagram</a>
```

## Template-Specific Customizations

### Restaurant/Cafe

- **Menu Items:** Update prices, dishes, and descriptions in the Menu section
- **Hours:** Modify opening hours in the Hours section
- **Location:** Update address and contact information

### Law Firm/Professional Services

- **Practice Areas:** Add or remove practice areas in the Services section
- **Attorney Profiles:** Update names, bios, and photos in the Attorneys section
- **Contact Form:** Customize the practice area dropdown

### Home Contractor

- **Service Descriptions:** Update service details and pricing
- **Gallery:** Replace project images with your own work
- **Testimonials:** Add real customer reviews
- **License Info:** Update contractor license and insurance details

### E-commerce/Product Landing

- **Product Images:** Replace with actual product photos
- **Pricing:** Update price and discount information
- **Product Specs:** Modify technical specifications
- **Order Form:** Customize order fields as needed

### Personal Portfolio

- **Bio:** Replace placeholder bio with your own
- **Projects:** Add your real projects with descriptions
- **Skills:** Update skill tags to match your expertise
- **Contact Info:** Update email, phone, and social links

## Deployment Options

### Option 1: GitHub Pages (Free)

1. Create a GitHub repository
2. Upload your `index.html` file
3. Go to Settings > Pages
4. Select main branch as source
5. Your site will be live at `https://yourusername.github.io/repo-name/`

### Option 2: Netlify (Free)

1. Sign up at [netlify.com](https://netlify.com)
2. Drag and drop your folder onto the dashboard
3. Your site is instantly live with HTTPS

### Option 3: Vercel (Free)

1. Sign up at [vercel.com](https://vercel.com)
2. Install Vercel CLI: `npm i -g vercel`
3. Run `vercel` in your project directory
4. Follow the prompts

### Option 4: Traditional Hosting

Upload files via FTP/SFTP to any web hosting provider:
- Bluehost
- HostGator
- GoDaddy
- SiteGround

## Best Practices

### Performance

- Compress images before uploading (use TinyPNG, ImageOptim)
- Use WebP format for better compression
- Keep image file sizes under 200KB each
- Minify HTML if needed (optional)

### SEO

- Update all meta tags with relevant keywords
- Add alt text to all images
- Use descriptive headings (H1, H2, H3)
- Ensure mobile responsiveness (built-in with Tailwind)

### Accessibility

- Maintain sufficient color contrast
- Ensure keyboard navigation works
- Use semantic HTML elements
- Test with screen readers

### Mobile Optimization

- All templates are mobile-first by default
- Test on multiple screen sizes
- Ensure touch targets are at least 44x44 pixels

## Need Help?

If you need assistance with customization or want a completely custom design, contact us:

- Email: contact@example.com
- Visit: https://github.com/guiltyfalcon/ai-portfolio

## License

All demo templates are free to use and modify for personal or commercial projects. No attribution required.