import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TeacherSignupComponent } from './teacher-signup.component';

describe('TeacherSignupComponent', () => {
  let component: TeacherSignupComponent;
  let fixture: ComponentFixture<TeacherSignupComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ TeacherSignupComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(TeacherSignupComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
