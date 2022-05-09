import { Component, OnInit } from '@angular/core';

import { CourseHttpService } from '../course-http.service';
import { Router } from '@angular/router';
import { Course } from '../models';

@Component({
  selector: 'app-courses',
  templateUrl: './courses.component.html',
  styleUrls: ['./courses.component.css']
})
export class CoursesComponent implements OnInit {
  private limit: number = 9;
  private skip: number = 0;
  courses: Course[] = [];

  constructor(
    private course_http: CourseHttpService,
    private router: Router
  ) { }

  ngOnInit(): void {
    this.getCourses();
  }

  getCourses(): void {
    this.course_http.getCourses(this.limit, this.skip).subscribe({
      next: (courses: Course[]) => {
        this.skip += this.limit;
        this.courses = courses;
      }
    })
  }
}
