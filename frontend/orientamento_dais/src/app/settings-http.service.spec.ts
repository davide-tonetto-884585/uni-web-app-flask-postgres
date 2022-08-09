import { TestBed } from '@angular/core/testing';

import { SettingsHttpService } from './settings-http.service';

describe('SettingsHttpService', () => {
  let service: SettingsHttpService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(SettingsHttpService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
