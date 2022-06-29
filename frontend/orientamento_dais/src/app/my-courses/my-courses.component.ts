import { Component, OnInit } from '@angular/core';

import { Course, ProgCourse, Lesson, Aula } from '../models';
import { CourseHttpService } from '../course-http.service';
import { UserHttpService } from '../user-http.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-my-courses',
  templateUrl: './my-courses.component.html',
  styleUrls: ['./my-courses.component.css']
})
export class MyCoursesComponent implements OnInit {
  courses: Course[] = [];

  constructor(
    private user_http: UserHttpService,
    private course_http: CourseHttpService,
    private router: Router
  ) { }

  ngOnInit(): void {
    if (!this.user_http.isLogged()) {
      this.router.navigate(['/login']);
    } else {
      let id = this.user_http.getId();

      if (this.user_http.isStudent() && id) {
        this.course_http.getInscriptionsStudent(id).subscribe({
          next: (corsi: Course[]) => {
            this.courses = corsi;
          }
        })
      } else if (this.user_http.isTeacher() && id) {
        this.course_http.getCorsiDocente(id).subscribe({
          next: (corsi: Course[]) => {
            this.courses = corsi;
          }
        })
      }
    }
  }

}
