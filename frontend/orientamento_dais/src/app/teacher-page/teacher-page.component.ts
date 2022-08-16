import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { CourseHttpService } from '../course-http.service';
import { BACKEND_URL } from '../globals';
import { Course } from '../models';
import { UserDataHttpService } from '../user-data-http.service';
import { UserHttpService } from '../user-http.service';

@Component({
  selector: 'app-teacher-page',
  templateUrl: './teacher-page.component.html',
  styleUrls: ['./teacher-page.component.css']
})
export class TeacherPageComponent implements OnInit {
  teacher_id: any;
  teacher: any;
  teacher_courses: Course[] = [];
  BACKEND_URL: string = BACKEND_URL;

  constructor(
    private activatedRoute: ActivatedRoute,
    private user_data_http: UserDataHttpService,
    private course_http: CourseHttpService
  ) { }

  ngOnInit(): void {
    this.activatedRoute.paramMap.subscribe(params => {
      this.teacher_id = params.get('id');
    });

    this.user_data_http.getUserData(this.teacher_id).subscribe({
      next: (res) => {
        this.teacher = { ...this.teacher, ...res };
      }
    });

    this.user_data_http.getTeacherData(this.teacher_id).subscribe({
      next: (res) => {
        this.teacher = { ...this.teacher, ...res };
      }
    });

    this.course_http.getCorsiDocente(this.teacher_id).subscribe({
      next: (courses) => {
        this.teacher_courses = courses;
      }
    })
  }

  counter(i: number) {
    let res = new Array(i);
    for (let ind = 0; ind < i; ind++) {
      res[ind] = ind;
    }

    return res;
  }
}
