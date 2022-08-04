import { Component, OnInit } from '@angular/core';

import { CourseHttpService } from '../course-http.service';
import { Router } from '@angular/router';
import { Course } from '../models';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css'],
  providers: [
    { provide: CourseHttpService, useClass: CourseHttpService }
  ]
})
export class HomeComponent implements OnInit {
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
      next: (res: any) => {
        this.skip += this.limit;
        this.courses = res.corsi;
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
