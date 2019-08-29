from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages

from .models import Classroom, Student
from .forms import ClassroomForm, SignupForm, SigninForm, StudentForm


def signup(request):
    form = SignupForm()
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(user.password)
            user.save()
            login(request, user)
            return redirect("classroom-list")
    context = {
        "form":form,
    }
    return render(request, 'signup.html', context)

def signin(request):
    form = SigninForm()
    if request.method == 'POST':
        form = SigninForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            auth_user = authenticate(username=username, password=password)
            if auth_user is not None:
                login(request, auth_user)
                return redirect('classroom-list')
    context = {
        "form":form
    }
    return render(request, 'signin.html', context)

def signout(request):
    logout(request)
    return redirect("signin")


def classroom_list(request):
	classrooms = Classroom.objects.all()
	context = {
		"classrooms": classrooms,
	}
	return render(request, 'classroom_list.html', context)


def classroom_detail(request, classroom_id):
	classroom = Classroom.objects.get(id=classroom_id)
	context = {
		"classroom": classroom,
		"students": classroom.students.filter(classroom = classroom).order_by('name', '-exam_grade'),
	}
	return render(request, 'classroom_detail.html', context)


def classroom_create(request):

	if request.user.is_anonymous:
		messages.warning(request, "You must login first!")
		return redirect('signin')

	form = ClassroomForm()
	if request.method == "POST":
		form = ClassroomForm(request.POST, request.FILES or None)
		if form.is_valid():
			classroom = form.save(commit = False)
			classroom.teacher = request.user
			classroom.save()
			messages.success(request, "Class is Successfully Created!")
			return redirect('classroom-list')
		print (form.errors)
	context = {
	"form": form,
	}
	return render(request, 'create_classroom.html', context)


def classroom_update(request, classroom_id):
	classroom = Classroom.objects.get(id=classroom_id)

	if classroom.teacher != request.user:
		messages.warning(request, "You have no access!")
		return redirect("classroom-list")

	form = ClassroomForm(instance=classroom)
	if request.method == "POST":
		form = ClassroomForm(request.POST, request.FILES or None, instance=classroom)
		if form.is_valid():
			form.save()
			messages.success(request, "Successfully Edited!")
			return redirect('classroom-list')
		print (form.errors)
	context = {
	"form": form,
	"classroom": classroom,
	}
	return render(request, 'update_classroom.html', context)


def classroom_delete(request, classroom_id):
	classroom = Classroom.objects.get(id=classroom_id)

	if classroom.teacher != request.user:
		messages.warning(request, "You have no access!")
		return redirect("classroom-list")

	classoom.delete()
	messages.success(request, "Successfully Deleted!")
	return redirect('classroom-list')

def student_add(request, classroom_id):
    classroom_obj = Classroom.objects.get(id=classroom_id)
    if request.user != classroom_obj.teacher:
    	messages.warning(request, "You have no access!")
    	return redirect ('classroom-list')
    form = StudentForm()
    if request.method == "POST":
        form = StudentForm(request.POST)
        if form.is_valid():
            student_obj = form.save(commit=False)
            student_obj.classroom = classroom_obj
            student_obj.save()
            return redirect(classroom_obj)
    context = {
        "form":form,
        'classroom': classroom_obj,
    }

    
    return render(request, 'student_add.html', context)


def student_update(request, student_id):
	student = Student.objects.get(id=student_id)

	if student.classroom.teacher != request.user:
		messages.warning(request, "You have no access!")
		return redirect("classroom-list")

	form = StudentForm(instance=student)
	if request.method == "POST":
		form = StudentForm(request.POST, request.FILES or None, instance=student)
		if form.is_valid():
			form.save()
			messages.success(request, "Successfully Edited!")
			return redirect('classroom-detail', student.classroom.id)
		print (form.errors)
	context = {
	"form": form,
	"student": student,
	}
	return render(request, 'update_student.html', context)


def student_delete(request, student_id):
	student = Student.objects.get(id=student_id)

	if student.classroom.teacher != request.user:
		messages.warning(request, "You have no access!")
		return redirect("classroom-list")

	student.delete()
	messages.success(request, "Successfully Deleted!")
	return redirect('classroom-detail', student.classroom.id)
