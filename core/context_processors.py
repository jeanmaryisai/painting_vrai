from .models import Setting

def settings_context(request):
    try :
        print(Setting.objects.get(show=True).home_painting_list_1.slug)
        return {
            'setting': Setting.objects.get(show=True)
        }
    except Setting.DoesNotExist:
        return {}
