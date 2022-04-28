import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ActivateProfileComponent } from './activate-profile.component';

describe('ActivateProfileComponent', () => {
  let component: ActivateProfileComponent;
  let fixture: ComponentFixture<ActivateProfileComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ActivateProfileComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ActivateProfileComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
