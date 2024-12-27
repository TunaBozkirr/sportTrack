from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.contrib import messages
from datetime import date, timedelta
from django.db.models import Sum
from .models import Group, Membership, Activity



# Modeller
from .models import Group, Membership, Activity


def home_view(request):
    """
    Ana sayfa:
      - Kullanıcı giriş yapmamışsa: basit login formu gösterir (action="{% url 'login' %}")
      - Giriş yapmışsa: son 10 aktiviteyi listeler ve yeni aktivite ekleme formu sunar.
    """
    if request.user.is_authenticated:
        activities = Activity.objects.filter(user=request.user).order_by('-date')[:10]
        context = {
            'activities': activities
        }
        return render(request, 'core/home.html', context)
    else:
        return render(request, 'core/home.html')


def register_view(request):
    """
    Kullanıcı kayıt fonksiyonu:
      - POST: Kullanıcı adı ve parolayı alıp User oluşturur.
      - GET: Kayıt formunu gösterir.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request, "Kullanıcı adı ve parola zorunludur.")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Bu kullanıcı adı zaten alınmış.")
            return redirect('register')

        user = User.objects.create_user(username=username, password=password)
        user.save()
        login(request, user)
        messages.success(request, "Başarıyla kayıt oldunuz ve giriş yaptınız!")
        return redirect('home')

    return render(request, 'core/register.html')


@login_required
def create_group_view(request):
    """
    Yeni bir grup oluşturma ve otomatik üye yapma.
    """
    if request.method == 'POST':
        group_name = request.POST.get('group_name')
        if group_name:
            new_group = Group.objects.create(name=group_name)
            Membership.objects.create(user=request.user, group=new_group)
            return redirect('list_groups')
    return render(request, 'core/create_group.html')


@login_required
def join_group_view(request, group_id):
    """
    Kullanıcı belirtilen group_id'li gruba katılır.
    Zaten üyeyse tekrar ekleme yapmaz.
    """
    group = get_object_or_404(Group, id=group_id)
    membership, created = Membership.objects.get_or_create(user=request.user, group=group)

    if created:
        messages.success(request, f"{group.name} grubuna başarıyla katıldınız!")
    else:
        messages.info(request, f"{group.name} grubuna zaten üyeysiniz.")

    return redirect('list_groups')



@login_required
def add_activity_view(request):
    """
    Yeni aktivite ekleme fonksiyonu.
    """
    if request.method == 'POST':
        activity_date_str = request.POST.get('activity_date')
        description = request.POST.get('description')
        duration = request.POST.get('duration')


        if not activity_date_str or not description:
            messages.error(request, "Tarih ve açıklama zorunludur.")
            return redirect('home')

        try:
            activity_date = date.fromisoformat(activity_date_str)
        except ValueError:
            messages.error(request, "Geçersiz tarih formatı!")
            return redirect('home')

        Activity.objects.create(
            user=request.user,
            date=activity_date,
            description=description,
            duration = duration
        )
        messages.success(request, "Aktivite eklendi!")
        return redirect('home')

    return redirect('home')


@login_required
def list_groups_view(request):
    all_groups = Group.objects.all()
    my_groups = Group.objects.filter(membership__user=request.user)  # Kullanıcının grupları

    for group in all_groups:
        # Üye olup olmadığını kontrol et
        group.is_member = group.membership_set.filter(user=request.user).exists()

    context = {
        'all_groups': all_groups,
        'my_groups': my_groups,  # Kullanıcının gruplarını şablona ekleyelim
    }
    return render(request, 'core/list_groups.html', context)


@login_required
def group_detail_view(request, group_id):
    # Grup kontrolü
    group = get_object_or_404(Group, id=group_id)

    # Kullanıcının gruba üyeliğini kontrol et
    is_member = Membership.objects.filter(user=request.user, group=group).exists()
    if not is_member:
        messages.error(request, "Bu grubun detaylarını görebilmek için önce gruba katılmalısınız.")
        return redirect('list_groups')  # Kullanıcıyı grup listesine yönlendir

    # Haftalık tarih aralığını hesapla (Pazartesi - Pazar)
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())  # Haftanın Pazartesi günü
    end_of_week = start_of_week + timedelta(days=6)  # Haftanın Pazar günü
    week_days = [start_of_week + timedelta(days=i) for i in range(7)]  # Pazartesi'den Pazar'a tarih listesi

    # Üyelerin aktiviteleri
    memberships = Membership.objects.filter(group=group).select_related('user')
    user_activities = []
    for membership in memberships:
        user = membership.user
        daily_activities = []
        weekly_total_duration = 0
        for day in week_days:
            activity = Activity.objects.filter(user=user, date=day).aggregate(total_duration=Sum('duration'))
            duration = activity['total_duration'] or 0
            weekly_total_duration += duration
            daily_activities.append({
                'date': day,
                'duration': duration,
            })
        user_activities.append({
            'user': user,
            'daily_activities': daily_activities,
            'weekly_total_duration': weekly_total_duration,
        })

    # Haftalık toplam süreye göre sıralama (Büyükten Küçüğe)
    user_activities.sort(key=lambda x: x['weekly_total_duration'], reverse=True)

    # Sıralı listeyi enumerate ile kullanıcıya sıra numarası ekleyerek güncelle
    user_activities = [
        {'rank': i + 1, **activity}  # Sıra numarasını 'rank' anahtarına ekle
        for i, activity in enumerate(user_activities)
    ]

    context = {
        'group': group,
        'user_activities': user_activities,
        'week_days': week_days,  # Haftanın günlerini sırayla gönder
    }
    return render(request, 'core/group_detail.html', context)







def custom_logout_view(request):
    """
    Logout işlemi (GET isteğini destekler).
    """
    print("Custom Logout View Çalıştı!")  # DEBUG
    if request.method == 'GET':
        logout(request)
        return redirect('/')
    else:
        return HttpResponseNotAllowed(['GET'])

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Group, Membership

@login_required
def leave_group_view(request, group_id):
    """
    Kullanıcı belirtilen gruptan ayrılır.
    Eğer zaten üye değilse hata mesajı gösterir.
    """
    group = get_object_or_404(Group, id=group_id)

    # Kullanıcının üyeliğini kontrol et
    membership = Membership.objects.filter(user=request.user, group=group).first()
    if membership:
        membership.delete()  # Üyeliği sil
        messages.success(request, f"{group.name} grubundan başarıyla ayrıldınız.")
    else:
        messages.error(request, "Bu gruba üye değilsiniz.")

    return redirect('list_groups')  # Grup listesi sayfasına yönlendir

