import { TestBed } from '@angular/core/testing';

import { UserDataHttpService } from './user-data-http.service';

describe('UserDataHttpService', () => {
  let service: UserDataHttpService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(UserDataHttpService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
