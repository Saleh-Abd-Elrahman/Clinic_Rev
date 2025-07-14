from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

def render_lang(request, template_name, context=None):
    if context is None:
        context = {}
    
    # Templates that should always be in English (admin/coordinator interfaces)
    english_only_templates = [
        "patient_start.html",
        "admin_doctors.html", 
        "admin_reviews.html",
        "admin_survey.html",
        "base.html",
        "index.html",
        "main_selection.html",
        "patient_review.html"
    ]
    
    # If it's an English-only template, render from root templates directory
    if template_name in english_only_templates:
        return templates.TemplateResponse(template_name, {"request": request, **context})
    
    # For patient-facing templates that support Arabic, use language-specific rendering
    lang = request.session.get("lang", "en")
    return templates.TemplateResponse(f"{lang}/{template_name}", {"request": request, **context})